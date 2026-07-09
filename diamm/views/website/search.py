from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import generics, response, status

from diamm.helpers.solr_pagination import (
    PageRangeOutOfBoundsException,
    SolrPaginator,
)
from diamm.search import (
    SearchQueryParams,
    SearchSolrService,
    SolrConnectionError,
    SolrResponseError,
    SolrTimeoutError,
)


class SearchView(generics.GenericAPIView):
    template_name = "website/search/search.jinja2"
    search_service = SearchSolrService()

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs) -> response.Response:
        params = SearchQueryParams.from_request(request)
        solr_request = self.search_service.build(
            params, is_staff=getattr(request.user, "is_staff", False)
        )

        try:
            paginator = SolrPaginator(
                solr_request.query,
                solr_request.filters,
                solr_request.exclusive_filters,
                solr_request.sorts,
                request,
                request_context=solr_request.request_context,
            )
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

        try:
            page = paginator.page(params.page)
        except PageRangeOutOfBoundsException:
            # If requesting past the number of pages, punt the user back to page 1.
            page = paginator.page(1)

        return response.Response(page.get_paginated_response())
