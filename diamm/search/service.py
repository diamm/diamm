from dataclasses import dataclass

import ujson
from django.conf import settings

from diamm.search.query_params import FilterValue, SearchQueryParams

type RequestContextValue = str | int | list[str] | list[object]


@dataclass(frozen=True)
class SearchSolrRequest:
    query: str
    filters: dict[str, FilterValue]
    exclusive_filters: dict[str, FilterValue]
    sorts: str
    request_context: dict[str, RequestContextValue]


def build_search_solr_request(
    params: SearchQueryParams, *, is_staff: bool
) -> SearchSolrRequest:
    filters: dict[str, FilterValue] = dict(params.filters)
    exclusive_filters: dict[str, FilterValue] = dict(params.exclusive_filters)
    sorts: list[str] = ["score desc"]

    filters["{!tag=type}type"] = settings.SOLR["SEARCH_TYPES"]
    if not is_staff:
        filters["public_b"] = True

    type_query = params.type_query
    if type_query and type_query in settings.SOLR["TYPE_SORTS"]:
        sorts.append(settings.SOLR["TYPE_SORTS"][type_query])
    else:
        sorts.append("display_name_s asc")

    if params.query and type_query == "all":
        filters["{!tag=type}type"] = settings.SOLR["SEARCH_TYPES"]
    elif type_query and type_query in settings.SOLR["SEARCH_TYPES"]:
        filters["{!tag=type}type"] = type_query
    elif type_query == "sources_with_images":
        filters["{!tag=type}type"] = "source"
        filters["{!tag=type}source_with_images_b"] = True

    if "anonymous_b" in filters:
        sorts[0] = "title_ans asc"

    request_context: dict[str, RequestContextValue] = {
        "q.op": settings.SOLR["DEFAULT_OPERATOR"],
        "facet": "true",
        "facet.field": settings.SOLR["FACET_FIELDS"],
        "facet.mincount": 1,
        "facet.limit": -1,
        "json.nl": "arrmap",
        "json.facet": ujson.dumps(settings.SOLR["JSON_FACETS"]),
        "facet.pivot": settings.SOLR["FACET_PIVOTS"],
        "hl": "true",
        "defType": "edismax",
        "qf": settings.SOLR["FULLTEXT_QUERYFIELDS"],
        "bq": ["type:source^10", "type:archive^5", "type:person^1"],
        **settings.SOLR["FACET_SORT"],
    }

    return SearchSolrRequest(
        query=params.query,
        filters=filters,
        exclusive_filters=exclusive_filters,
        sorts=", ".join(sorts),
        request_context=request_context,
    )
