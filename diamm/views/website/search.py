from django.conf import settings
from rest_framework import generics
from rest_framework import response
from rest_framework import status
from diamm.helpers.solr_pagination import SolrPaginator, SolrResultException


class SearchView(generics.GenericAPIView):
    template_name = "website/search/search.jinja2"

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', None)
        filters = {}
        sorts = {}

        if not query:
            return response.Response({})

        type_query = request.GET.get('type', None)

        if not type_query or type_query == "all":
            filters.update({
                'type': settings.SOLR['SEARCH_TYPES']
            })
        elif type_query and type_query in settings.SOLR['SEARCH_TYPES']:
            filters.update({
                'type': type_query
            })
        # else ignore any invalid type filter settings...

        try:
            page_num = int(request.GET.get('page', 1))
        except ValueError:
            page_num = 1

        try:
            paginator = SolrPaginator(query, filters, sorts, request)
            page = paginator.page(page_num)
        except SolrResultException as e:
            # We assume that an exception raised by Solr is the result of a bad request by the client,
            #  so we bubble up a 400 with a message about why it went wrong.
            return response.Response({'message': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

        return response.Response(page.get_paginated_response())
