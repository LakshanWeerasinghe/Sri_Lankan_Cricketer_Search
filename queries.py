def build_best_or_worst_intent_query(keywords_str, intent_categories, size, is_best, role_filter, bowling_style_filter):
    order = "desc"
    if not is_best:
        order = "asc"

    batter_intents = ["batter", "batsmen", "player", "runs", "පිතිකරුවන්", "ක්‍රීඩකයා", "ලකුණු"]
    bowler_intents = ["bowler", "player", "wicket", "පන්දු", "යවන්නා", "කඩුලු"]

    # deciding the order category
    sort_query = {}
    if not set(intent_categories).isdisjoint(batter_intents):
        sort_query["odi_runs"] = {"order": order}
    if not set(intent_categories).isdisjoint(bowler_intents):
        sort_query["odi_wickets"] = {"order": order}

    if size is None:
        size = 10

    query = []

    # appending filter queries
    query.extend(get_filtering_sub_queries(role_filter, bowling_style_filter))

    # appending text search query
    if keywords_str:
        query.append({"multi_match": {"query": keywords_str}})
    else:
        query.append({"match_all": {}})

    return {
        "size": size,
        "query": {
            "bool": {
                "must": query
            }
        },
        "sort": sort_query,
        "aggs": {
            "bowling_style": {
                "terms": {
                    "field": "bowling_style_si.keyword",
                    "size": 10
                }
            },
            "role": {
                "terms": {
                    "field": "role_si.keyword",
                    "size": 10
                }
            }
        }
    }


def build_intent_category_query(size, keywords_str, boosting_fields, role_filter, bowling_style_filter):
    if not size:
        size = 20

    query = []

    # appending filter queries
    query.extend(get_filtering_sub_queries(role_filter, bowling_style_filter))

    # appending the phrase query
    if len(keywords_str) == 0:
        query.append({"match_all": {}})
    else:
        query.append({
            "multi_match": {
                "query": keywords_str,
                "operator": "or",
                "type": "best_fields",
                "fields": boosting_fields
            }
        })

    return {
        "size": size,
        "query": {
            "bool": {
                "must": query
            }
        },
        "aggs": {
            "bowling_style": {
                "terms": {
                    "field": "bowling_style_si.keyword",
                    "size": 10
                }
            },
            "role": {
                "terms": {
                    "field": "role_si.keyword",
                    "size": 10
                }
            }
        }
    }


def build_phrase_query(phrase, role_filter, bowling_style_filter):
    query = []

    # appending filter queries
    query.extend(get_filtering_sub_queries(role_filter, bowling_style_filter))

    # appending the phrase query
    query.append({
        "multi_match": {
            "query": phrase,
            "type": "phrase"
        }
    })

    return {
        "query": {
            "bool": {
                "must": query
            }
        },
        "aggs": {
            "bowling_style": {
                "terms": {
                    "field": "bowling_style_si.keyword",
                    "size": 10
                }
            },
            "role": {
                "terms": {
                    "field": "role_si.keyword",
                    "size": 10
                }
            }
        }
    }


def build_no_intent_query(keywords_str, role_filter, bowling_style_filter):
    query = []

    # appending filter queries
    query.extend(get_filtering_sub_queries(role_filter, bowling_style_filter))

    # appending the phrase query
    query.append(get_no_intent_sub_query(keywords_str))

    return {
        "size": 10,
        "query": {
            "bool": {
                "must": query
            }
        },
        "aggs": {
            "bowling_style": {
                "terms": {
                    "field": "bowling_style_si.keyword",
                    "size": 10
                }
            },
            "role": {
                "terms": {
                    "field": "role_si.keyword",
                    "size": 10
                }
            }
        }
    }


def get_no_intent_sub_query(keywords_str):
    return {
        "multi_match": {
            "query": keywords_str,
            "fields": ["full_name_en^3", "birthday", "batting_style_en^1.5", "bowling_style_en^1.5",
                       "role_en^3", "education_en^2.5", "biography_en", "international_carrier_en",
                       "test_debut_en^1.5", "odi_debut_en^1.5", "t20i_debut_en^1.5", "full_name_si^3",
                       "batting_style_si^1.5", "bowling_style_si^1.5", "role_si^1.5", "education_si^2",
                       "biography_si", "international_carrier_si", "test_debut_si^1.5", "odi_debut_si^1.5",
                       "t20i_debut_si^1.5"
                       ]
        }
    }


def get_filtering_sub_queries(role_filter, bowling_style_filter):
    sub_query = []
    if len(role_filter) != 0:
        for role in role_filter:
            sub_query.append({"match": {"role_si": role["key"]}})
    if len(bowling_style_filter) != 0:
        for bowling_style in bowling_style_filter:
            sub_query.append({"match": {"bowling_style_si": bowling_style["key"]}})
    return sub_query
