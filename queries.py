def multi_match_any_and_sort(size, sort_query):
    return {
        "size": size,
        "query": {
            "match_all": {
            }
        },
        "sort": sort_query
    }


def bool_multi_match_and_sort(size, sort_query, query, fields):
    return {
        "size": size,
        "query": {
            "bool": {
                "must": [{
                    "multi_match": {
                        "query": query
                    }
                }]
            }
        },
        "sort": sort_query
    }


def multi_match(size, query, boosting_fields):
    return {
        "size": size,
        "query": {
            "multi_match": {
                "query": query,
                "operator": "or",
                "type": "best_fields",
                "fields": boosting_fields
            }
        },
        "aggs": {
            "batting_style": {
                "terms": {
                    "field": "batting_style_si.keyword",
                    "size": 15
                }
            },
            "bowling_style": {
                "terms": {
                    "field": "bowling_style_si.keyword",
                    "size": 15
                }
            },
            "role": {
                "terms": {
                    "field": "role_si.keyword",
                    "size": 15
                }
            }
        }
    }


def phrase_query(phrase):
    return {
        "query": {
            "multi_match": {
                "query": phrase,
                "type": "phrase"
            }
        }
    }
