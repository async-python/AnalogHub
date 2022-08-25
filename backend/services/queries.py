from core.config import AppSettings
from services.enums import Maker, SearchType

conf = AppSettings()

page_num_params = {'default': 0, 'ge': 0}
page_size_params = {'default': 20, 'ge': 1}

page_search_params = {
    'page_number': 0,
    'page_size': 2
}


def get_base_multimatch_query(
        request: str, search_fields: list[str], search_type: SearchType):
    query = {
        "query": {
            "bool": {
                "must": {
                    search_type: {
                        "query": request,
                        "fields": search_fields
                    }
                }
            }
        }
    }
    return query


def get_multimatch_query(
        request: str,
        search_fields: list[str],
        maker: str = None,
        search_type: SearchType = SearchType.multi_match):
    query = get_base_multimatch_query(request, search_fields, search_type)
    if maker:
        maker_filter = get_maker_filter(maker)
        query["query"]["bool"] = query["query"]["bool"] | maker_filter
        return query
    return query


def get_maker_filter(maker: str):
    filter_term = "term"
    if maker == Maker.PRIORITY:
        maker = conf.priority_brands
        filter_term += "s"
    return {"filter": {filter_term: {"maker": maker}}}


def get_pagination_query(page_number: int, page_size: int):
    return {"from": page_number * page_size, "size": page_size}
