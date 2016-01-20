from django.conf import settings
from rest_framework import generics
from rest_framework import renderers
from rest_framework import response
from diamm.models.data.source import Source
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.serializers.website.source import SourceListSerializer
from diamm.helpers.solr_pagination import SolrPaginator
from django.core.paginator import EmptyPage, PageNotAnInteger
import scorched

# class Facet:
#     def serialize(self):
#         fields = OrderedDict(self.fields)
#         return {
#             "name": self.name,
#             "fields": fields
#         }
#
#
# class TypeFilterFacet(Facet):
#     name = "Type"
#     fields = (
#         ('all', 'All'),
#         (settings.SOLR_SOURCE_TYPE, 'Source'),
#         ('person', 'Person'),
#         ('composition', 'Composition'),
#         ('place', 'Place'),
#     )


class SearchView(generics.GenericAPIView):
    template_name = "website/search/search.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    queryset = Source.objects.all()
    serializer_class = SourceListSerializer

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', None)
        rtype = request.GET.get('type', None)

        if not query:
            return response.Response({})

        conn = scorched.SolrInterface(settings.SOLR['SERVER'])

        solrq = conn.query(query)


        if rtype:
            solrq = solrq.filter(type=rtype)

        paginator = SolrPaginator(solrq, request)
        page_num = request.GET.get('page', 1)

        try:
            page = paginator.page(page_num)
        except PageNotAnInteger:
            # If an invalid page number was passed in, show the first page of results
            page = paginator.page()

        return response.Response(page.get_paginated_response())
