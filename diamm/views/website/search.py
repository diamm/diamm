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
        if 'composers_ss' in request.GET:
            filters.update({
                'composers_ss': "\"{0}\"".format(request.GET.get('composers_ss'))
            })


        if type_query in settings.SOLR['TYPE_SORTS'].keys():
            sorts.append(settings.SOLR['TYPE_SORTS'][type_query])
        else:
            sorts.append('archive_city_s asc')

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
        except PageRangeOutOfBoundsException:
            # If requesting past the number of pages, punt the user back to page 1.
            page = paginator.page(1)

        return response.Response(page.get_paginated_response())
