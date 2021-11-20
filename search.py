from elasticsearch import Elasticsearch, ElasticsearchException

from queries import build_best_or_worst_intent_query, build_intent_category_query, build_phrase_query, \
    build_no_intent_query
from utils.utils import get_cosine_sim

from Settings import Settings
from utils.tokenizer import Tokenizer
from utils.player_images import get_player_images

es = Elasticsearch('http://localhost:9200')


def get_best_similarity(word, keywords):
    keywords_simi = []
    for keyword in keywords:
        keywords_simi.append(get_cosine_sim(word, keyword))
    max_value = max(keywords_simi)
    return max_value, keywords_simi.index(max_value)


def intent_classifier(keywords):
    print("======= intent classifying process begin =======")

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

    filter_word_indexes = []
    for term_index in range(len(keywords)):
        term = keywords[term_index]
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

    keywords_str = ''
    if _is_intent_best or _is_intent_worst or _is_intent_category:
        query_words = keywords
        result_words = []
        for word_index in range(len(query_words)):
            if word_index not in filter_word_indexes:
                result_words.append(query_words[word_index])

        keywords_str = ' '.join(result_words)

    print("======= intent classifying process end =======")
    return _is_intent_best, _is_intent_worst, _is_intent_category, _intent_categories, _intent_count, keywords_str


def search_text(keywords_str, role_filter, bowling_style_filter):
    print("======= search for normal text begin =======")
    print("keywords_str : {}".format(keywords_str))

    query = build_no_intent_query(keywords_str, role_filter, bowling_style_filter)

    print("search for normal text query : {}".format(query))
    results = None
    try:
        results = es.search(index='sri-lankan-cricketers', body=query)
    except ElasticsearchException as ex:
        print(ex.args)
    finally:
        print("======= search for normal text end =======")
        return results


def search_intent_category(keywords_str, intent_categories, size, role_filter, bowling_style_filter):
    print("======= search for intent category begin =======")
    print("keywords_str : {}".format(keywords_str))
    print("intent_categories : {}".format(intent_categories))
    print("size : {}".format(size))
    print("role_filter : {}".format(role_filter))
    print("bowling_style_filter : {}".format(bowling_style_filter))

    terms_map = {
        "batter": ["batting_style_en", "role_en", "batting_style_si"],
        "batsmen": ["batting_style_en", "role_en"],
        "bowler": ["bowling_style_en", "role_en"],
        "test": ["test_debut_en", "test_debut_si", "role_en", "role_si"],
        "odi": ["odi_debut_en", "odi_debut_si", "role_en", "role_si"],
        "t20": ["t20_debut_en", "t20_debut_si", "role_en", "role_si"],
        "player": ["odi_wickets", "batting_style_en", "batting_style_si", "role_en", "role_si"],
        "runs": ["batting_style_en", "batting_style_si", "role_en", "role_si"],
        "wicket": ["bowling_style_en", "bowling_style_si", "role_en", "role_si"],
        "පිතිකරුවන්": ["batting_style_en", "batting_style_si", "role_en", "role_si"],
        "පන්දු": ["bowling_style_en", "bowling_style_si", "role_en", "role_si"],
        "යවන්නා": ["bowling_style_en", "bowling_style_si", "role_en", "role_si"],
        "ක්‍රීඩකයා": ["odi_wickets", "batting_style_en", "batting_style_si",
                      "bowling_style_en", "bowling_style_si", "role_en", "role_si"],
        "ලකුණු": ["batting_style_en", "batting_style_si", "role_en", "role_si"],
        "කඩුලු": ["bowling_style_en", "bowling_style_si", "role_en", "role_si"]
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

    print(boosting_fields)
    query = build_intent_category_query(size, keywords_str, boosting_fields, role_filter, bowling_style_filter)

    print("search for normal text query : {}".format(query))
    results = None
    try:
        results = es.search(index='sri-lankan-cricketers', body=query)
    except ElasticsearchException as ex:
        print(ex.args)
    finally:
        print("======= search for normal text end =======")
        return results


def search_for_best_or_worst(keywords_str, intent_categories, size, is_best, role_filter, bowling_style_filter):
    print("======= search for best/worst intent begin =======")
    print("keywords_str : {}".format(keywords_str))
    print("intent_categories : {}".format(intent_categories))
    print("size : {}".format(size))
    print("is_best : {}".format(is_best))
    print("role_filter : {}".format(role_filter))
    print("bowling_style_filter : {}".format(bowling_style_filter))

    query = build_best_or_worst_intent_query(keywords_str, intent_categories, size, is_best, role_filter,
                                             bowling_style_filter)

    print("search for best/worst intent query : {}".format(query))
    results = None
    try:
        results = es.search(index='sri-lankan-cricketers', body=query)
    except ElasticsearchException as ex:
        print(ex.args)
    finally:
        print("======= search for best/worst intent end =======")
        return results


def search_phrase(phrase, role_filter, bowling_style_filter):
    print("======= search for phrase intent begin =======")
    print("phrase : {}".format(phrase))
    print("role_filter : {}".format(role_filter))
    print("bowling_style_filter : {}".format(bowling_style_filter))

    query = build_phrase_query(phrase, role_filter, bowling_style_filter)

    print("search for phrase intent final_query : {}".format(query))
    results = None
    try:
        results = es.search(index='sri-lankan-cricketers', body=query)
    except ElasticsearchException as ex:
        print(ex.args)
    finally:
        print("======= search for phrase intent end =======")
        return results


def show_results(result):
    hits = result.get('hits').get('hits')
    for result_index in range(len(hits)):
        player_details = hits[result_index].get('_source')
        print(player_details.get('full_name_en'))


def query_preprocessor(query):
    return Tokenizer.tokenize(query)


def post_processor(result):
    final_result = {}
    if not result:
        final_result['no_result'] = True
        return final_result, [], []

    hits = result.get('hits').get('hits')
    player_count = len(hits)
    final_result = {}
    roles = []
    bowling_styles = []
    if player_count == 0:
        final_result['no_result'] = True
    else:
        final_result['no_result'] = False
        final_result['player_count'] = player_count
        players = []

        for result_index in range(len(hits)):
            player = {}
            player_details = hits[result_index].get('_source')
            player['_id'] = hits[result_index].get('_id')
            player['full_name_en'] = player_details.get('full_name_en')
            player['full_name_si'] = player_details.get('full_name_si')
            player['batting_style_si'] = player_details.get('batting_style_si')
            player['bowling_style_si'] = player_details.get('bowling_style_si')
            player['odi_runs'] = player_details.get('odi_runs')
            player['odi_wickets'] = player_details.get('odi_wickets')
            players.append(player)

        final_result['players'] = players

        aggregations = result['aggregations']
        print(aggregations)
        roles = aggregations['role']['buckets']
        for role in roles:
            role['id'] = f'role-{roles.index(role)}'

        bowling_styles = aggregations['bowling_style']['buckets']
        for bowling_style in bowling_styles:
            bowling_style['id'] = f'bowling-style-{bowling_styles.index(bowling_style)}'

    return final_result, roles, bowling_styles


def search(user_query, role_filter=[], bowling_style_filter=[]):
    tokens, phrases = query_preprocessor(user_query)

    print(tokens, phrases)

    if len(phrases) > 0:
        search_result = search_phrase(phrases[0], role_filter, bowling_style_filter)
        return post_processor(search_result)

    is_intent_best, is_intent_worst, is_intent_category, \
    intent_categories, intent_count, keywords_str = intent_classifier(tokens)

    print(is_intent_best, is_intent_worst, is_intent_category, intent_categories, intent_count, keywords_str)
    if is_intent_best:
        search_result = search_for_best_or_worst(keywords_str, intent_categories, intent_count, True, role_filter,
                                                 bowling_style_filter)
    elif is_intent_worst:
        search_result = search_for_best_or_worst(keywords_str, intent_categories, intent_count, False, role_filter,
                                                 bowling_style_filter)
    elif intent_categories:
        search_result = search_intent_category(keywords_str, intent_categories, intent_count)
    else:
        keywords_str = ' '.join(tokens)
        search_result = search_text(keywords_str, role_filter, bowling_style_filter)

    return post_processor(search_result)


def get_player_by_id(player_id):
    print("======= get player details begin =======")
    print("player_id : {}".format(player_id))

    player = None
    try:
        results = es.get(index=Settings.index_name.value, id=player_id)
        player = results.get('_source')
        player["image_url"] = get_player_images()[player["website_url"]]

    except ElasticsearchException as ex:
        print(ex.args)
    finally:
        print("======= get player details begin end =======")
        return player
