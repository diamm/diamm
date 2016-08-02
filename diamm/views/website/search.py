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
                '{!tag=type}type': settings.SOLR['SEARCH_TYPES']
            })
        elif type_query and type_query in settings.SOLR['SEARCH_TYPES']:
            filters.update({
                '{!tag=type}type': type_query
            })
        elif type_query and type_query == "sources_with_images":
            filters.update({
                '{!tag=type}type': 'source',
                '{!tag=type}public_images_b': True
            })
        # else ignore any invalid type filter settings...

        geo_filter = {
            ('archive_country_s', 'country_s'): request.GET.get('country', None),
            ('archive_city_s', 'city_s'): request.GET.get('city', None),
            ('archive_s'): request.GET.get('archive', None)
        }
        # remove keys with None values and surrond values in quotes
        geo_filter = {k:'"{0}"'.format(v) for (k, v) in geo_filter.items() if v}
        if geo_filter:
            filters.update(geo_filter)

        genre_filter = request.GET.get('genre')
        if genre_filter:
            filters.update({'genres_ss': genre_filter})

        century_filter = request.GET.get('century')
        if century_filter:
            filters.update({
                'start_date_i': '[* TO {0}]'.format(century_filter),
                'end_date_i': '[{0} TO *]'.format(century_filter)})

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
