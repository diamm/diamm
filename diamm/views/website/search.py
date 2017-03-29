from django.conf import settings
from rest_framework import generics
from rest_framework import response
from rest_framework import status
from diamm.helpers.solr_pagination import SolrPaginator, SolrResultException, PageRangeOutOfBoundsException


class SearchView(generics.GenericAPIView):
    template_name = "website/search/search.jinja2"

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', None)
        filters = {}
        exclusive_filters = {}  # these will get ANDed... the others will get ORed
        sorts = []

        # On a blank query retrieve everything, but sort
        # by archive_city_s so that sources sort to the top.
        if not query:
            query = "*:*"

        filters.update({
            '{!tag=type}type': settings.SOLR['SEARCH_TYPES']
        })

        type_query = request.GET.get('type', None)

        # if we have an active query but want all types.
        if query and type_query == "all":
            filters.update({
                '{!tag=type}type': settings.SOLR['SEARCH_TYPES']
            })
            sorts.append('archive_city_s asc')

        elif type_query and type_query in settings.SOLR['SEARCH_TYPES']:
            filters.update({
                '{!tag=type}type': type_query
            })
        elif type_query and type_query == "sources_with_images":
            filters.update({
                '{!tag=type}type': 'source',
                '{!tag=type}public_images_b': True
            })

        if 'country_s' in request.GET:
            filters.update({
                'country_s': "\"{0}\"".format(request.GET.get('country_s'))
            })
        if 'city_s' in request.GET:
            filters.update({
                'city_s': "\"{0}\"".format(request.GET.get('city_s'))
            })

        if 'composer' in request.GET:
            exclusive_filters.update({
                'composers_ss': ["\"{0}\"".format(p.replace('"', r'\"')) for p in request.GET.getlist('composer')]
            })

        if 'genre' in request.GET:
            exclusive_filters.update({
                'genres_ss': ["\"{0}\"".format(p.replace('"', r'\"')) for p in request.GET.getlist('genre')]
            })

        if 'notation' in request.GET:
            exclusive_filters.update({
                'notations_ss': ["\"{0}\"".format(p.replace('"', r'\"')) for p in request.GET.getlist('notation')]
            })

        if 'sourcetype' in request.GET:
            exclusive_filters.update({
                "source_type_s": ["\"{0}\"".format(p.replace('"', r'\"')) for p in request.GET.getlist('sourcetype')]
            })

        if 'has_inventory' in request.GET:
            filters.update({
                'inventory_provided_b': request.GET.get('has_inventory', None)
            })

        if 'date_range' in request.GET:
            start, end = request.GET.get('date_range').split(",")
            filters.update({
                'facet_date_range_ii': "[{0} TO {1}]".format(start, end)
            })

        if 'anonymous' in request.GET:
            filters.update({
                'anonymous_b': request.GET.get('anonymous', None)
            })

        # adjusts the sorting for each type, but defaults to sorting empty queries
        # by archive_city so that sources sort to the top alphabetically by the
        # city where they are held.
        if type_query in settings.SOLR['TYPE_SORTS'].keys():
            sorts.append(settings.SOLR['TYPE_SORTS'][type_query])
        else:
            sorts.append('archive_city_s asc')

        try:
            page_num = int(request.GET.get('page', 1))
        except ValueError:
            page_num = 1

        try:
            paginator = SolrPaginator(query, filters, exclusive_filters, sorts, request)
            page = paginator.page(page_num)
        except SolrResultException as e:
            # We assume that an exception raised by Solr is the result of a bad request by the client,
            #  so we bubble up a 400 with a message about why it went wrong.
            return response.Response({'message': repr(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PageRangeOutOfBoundsException:
            # If requesting past the number of pages, punt the user back to page 1.
            page = paginator.page(1)

        return response.Response(page.get_paginated_response())
