from elasticsearch import Elasticsearch

from queries import bool_multi_match_and_sort, multi_match_any_and_sort, multi_match
from utils.utils import get_cosine_sim

es = Elasticsearch('http://localhost:9200')


def get_best_similarity(word, keywords):
    keywords_simi = []
    for keyword in keywords:
        keywords_simi.append(get_cosine_sim(word, keyword))
    max_value = max(keywords_simi)
    return max_value, keywords_simi.index(max_value)


def intent_classifier(search_term):
    best_terms = ["top", "best", "super", "පට්ට", "පට්ටම", "සුපිරිම", "හොඳම", "හොදම"]
    worst_terms = ["worst", "bad", "ugly", "චොරම", "චාටර්ම"]
    category_terms = ["batter", "batsmen", "bowler", "player", "runs", "wicket", "debut", "මංගල", "තරගය",
                      "odi", "t20", "test", "පිතිකරුවන්", "පන්දු", "යවන්නා", "ක්‍රීඩකයා", "තරඟය",
                      "ලකුණු", "කඩුලු"]

    _is_intent_best = False
    _is_intent_worst = False
    _is_intent_category = False
    _intent_categories = []
    _intent_count = None

    search_terms = search_term.split()
    filter_word_indexes = []
    for term_index in range(len(search_terms)):
        term = search_terms[term_index]
        best_simi = get_best_similarity(term, best_terms)
        worst_simi = get_best_similarity(term, worst_terms)
        category_simi = get_best_similarity(term, category_terms)

        if best_simi[0] > 0.85:
            _is_intent_best = True
            filter_word_indexes.append(term_index)

        if worst_simi[0] > 0.85:
            _is_intent_worst = True
            filter_word_indexes.append(term_index)

        if category_simi[0] > 0.85:
            _is_intent_category = True
            _intent_categories.append(category_terms[category_simi[1]])
            filter_word_indexes.append(term_index)

        if term.isnumeric():
            _intent_count = int(term)
            filter_word_indexes.append(term_index)

        if term == "player":
            _intent_count = 1

    result_word = ''
    if _is_intent_best or _is_intent_worst or _is_intent_category:
        query_words = search_term.split()
        result_words = []
        for word_index in range(len(query_words)):
            if word_index not in filter_word_indexes:
                result_words.append(query_words[word_index])

        result_word = ' '.join(result_words)

    print(result_word)
    return _is_intent_best, _is_intent_worst, _is_intent_category, _intent_categories, _intent_count, result_word


def search_text(user_query):
    query = {
        "size": 10,
        "query": {
            "multi_match": {
                "query": user_query,
                "fields": ["full_name_en^3", "birthday", "batting_style_en^1.5", "bowling_style_en^1.5", "role_en^3",
                           "education_en^2.5", "biography_en", "international_carrier_en", "test_debut_en^1.5",
                           "odi_debut_en^1.5", "t20i_debut_en^1.5", "full_name_si^3", "batting_style_si^1.5",
                           "bowling_style_si^1.5", "role_si^1.5",
                           "education_si^2", "biography_si", "international_carrier_si", "test_debut_si^1.5",
                           "odi_debut_si^1.5", "t20i_debut_si^1.5"
                           ]
            }
        }
    }

    print(query)
    results = es.search(index='sri-lankan-cricketers', body=query)
    return results


def search_intent_category(resultword, intent_categories, size):
    terms_map = {
        "batter": ["batting_style_en", "role_en"],
        "batsmen": ["batting_style_en", "role_en"],
        "bowler": ["bowling_style_en", "role_en"],
        "test": ["test_debut_en"],
        "odi": ["odi_debut_en"],
        "t20": ["t20_debut_en"],
        "player": ["odi_runs", "odi_wickets"],
        "runs": ["odi_runs", "odi_wickets"],
        "wicket": ["odi_wickets"],
        "පිතිකරුවන්": ["odi_runs"],
        "පන්දු": ["odi_wickets"],
        "යවන්නා": ["odi_wickets"],
        "ක්‍රීඩකයා": ["odi_runs", "odi_wickets"],
        "ලකුණු": ["odi_runs"],
        "කඩුලු": ["odi_wickets"]
    }

    debut_intent_keywords = ["debut", "මංගල", "තරගය", "තරඟය"]

    boosting_fields = []
    for category in intent_categories:
        if len(list(set(debut_intent_keywords).intersection(set(intent_categories)))) > 0:
            if category in ["odi", "test", "t20"] and "debut":
                boosting_fields.append(f'{category}_debut_en^3')
                boosting_fields.append(f'{category}_debut_si^3')
            else:
                boosting_fields.extend(["test_debut_en", "odi_debut_en", "t20_debut_en"])
        elif category in ["odi", "test", "t20"] and "debut":
            continue
        else:
            boosting_fields.extend(terms_map.get(category))
    if not size:
        size = 20

    query = multi_match(size, resultword, boosting_fields)

    print(query)
    results = es.search(index='sri-lankan-cricketers', body=query)
    return results


def search_best(resultword, intent_categories, size, is_best):
    print(resultword, intent_categories, size, is_best)
    fields = []

    order = "desc"
    if not is_best:
        order = "asc"

    batter_intents = ["batter", "batsmen", "player", "runs", "පිතිකරුවන්", "ක්‍රීඩකයා", "ලකුණු"]
    bowler_intents = ["bowler", "player", "wicket", "පන්දු", "යවන්නා", "කඩුලු"]

    sort_query = {}
    if not set(intent_categories).isdisjoint(batter_intents):
        sort_query["odi_runs"] = {"order": order}
    if not set(intent_categories).isdisjoint(bowler_intents):
        sort_query["odi_wickets"] = {"order": order}

    if size is None:
        size = 10

    if resultword:
        query = bool_multi_match_and_sort(size, sort_query, resultword, fields)
    else:
        query = multi_match_any_and_sort(size, sort_query)

    print(query)
    results = es.search(index='sri-lankan-cricketers', body=query)
    return results


def show_results(result):
    hits = result.get('hits').get('hits')
    for result_index in range(len(hits)):
        player_details = hits[result_index].get('_source')
        print(player_details.get('full_name_en'))


def search(user_query):
    is_intent_best, is_intent_worst, is_intent_category, \
    intent_categories, intent_count, resultword = intent_classifier(user_query)

    print(is_intent_best, is_intent_worst, is_intent_category, intent_categories, intent_count, resultword)
    if is_intent_best:
        search_result = search_best(resultword, intent_categories, intent_count, True)
    elif is_intent_worst:
        search_result = search_best(resultword, intent_categories, intent_count, False)
    elif intent_categories:
        search_result = search_intent_category(resultword, intent_categories, intent_count)
    else:
        search_result = search_text(user_query)
    print(show_results(search_result))
    print(search_result)
    return search_result