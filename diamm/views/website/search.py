from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import generics, response, status

from diamm.helpers.solr import (
    PageRangeOutOfBoundsException,
    SolrConnectionError,
    SolrPaginator,
    SolrResponseError,
    SolrTimeoutError,
    build_search_query_params,
    build_search_solr_request,
)


class SearchView(generics.GenericAPIView):
    template_name = "website/search/search.jinja2"

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs) -> response.Response:
        params = build_search_query_params(request)
        solr_request = build_search_solr_request(
            params,
            is_staff=getattr(request.user, "is_staff", False),
        )

        try:
            paginator = SolrPaginator(solr_request, request)
            try:
                page = paginator.page(params.page)
            except PageRangeOutOfBoundsException:
                page = paginator.page(1)
        except SolrResponseError as exc:
            return response.Response(
                {"message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
                if exc.status_code and 400 <= exc.status_code < 500
                else status.HTTP_502_BAD_GATEWAY,
            )
        except (SolrConnectionError, SolrTimeoutError) as exc:
            return response.Response(
                {"message": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return response.Response(page.get_paginated_response())
