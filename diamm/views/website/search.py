from rest_framework import generics
from rest_framework import response
from rest_framework import status
from diamm.models.data.source import Source
from diamm.serializers.website.source import SourceListSerializer
from diamm.helpers.solr_pagination import SolrPaginator, SolrResultException

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
    queryset = Source.objects.all()
    serializer_class = SourceListSerializer

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', None)
        filters = {}
        sorts = {}

        if not query:
            return response.Response({})

        type_filt = request.GET.get('type', None)
        if type_filt:
            # Translate all to a wildcard.
            if type_filt == "all":
                type_filt = "*"
            filters.update({
                'type': type_filt
            })

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
