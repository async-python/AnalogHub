page_num_params = {'default': 0, 'ge': 0}
page_size_params = {'default': 20, 'ge': 1}

page_search_params = {
    'page_number': 0,
    'page_size': 2
}


def get_base_match_query(search_field: str, request: str):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: request}}
                ]
            }
        }
    }
    return query


def get_wildcard_query(search_fields: list[str], request: str, maker=None):
    query = {
        "query": {
            "bool": {
                "must": {
                    "query_string": {
                        "query": request,
                        "fields": search_fields
                    }
                }
            }
        }
    }
    if maker:
        filter = {"filter": {"term": {"maker": maker}}}
        query["query"]["bool"] = query["query"]["bool"] | filter
    return query


def get_multimatch_query(
        search_fields: list, request: str, maker: str = None, ):
    query = {
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": request,
                        "fields": search_fields
                    }
                }
            }
        }
    }
    if maker:
        filter = {"filter": {"term": {"maker": maker}}}
        query["query"]["bool"] = query["query"]["bool"] | filter
    return query


def get_pagination_query(page_number: int, page_size: int):
    return {"from": page_number * page_size, "size": page_size}
