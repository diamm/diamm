from rest_framework import generics
from rest_framework import response
from rest_framework import status
from rest_framework.reverse import reverse
from django.conf import settings
from drf_ujson.renderers import UJSONRenderer
import pysolr


class CanvasListData(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)

    def get(self, request, *args, **kwargs):
        return response.Response([])


class CanvasData(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)

    def get(self, request, *args, **kwargs):
        page_id = kwargs.get('page_id', None)
        if not page_id:
            return response.Response({'error': 'Page was not in request'}, status.HTTP_400_BAD_REQUEST)

        page_query = {
            "fq": ["type:page", "pk:{0}".format(page_id)]
        }
        conn = pysolr.Solr(settings.SOLR['SERVER'])
        page_res = conn.search("*:*", **page_query)

        if not page_res.hits > 0:
            return response.Response([])

        page = page_res.docs[0]
        page_items = page.get('items_ii', None)

        if not page_items:
            return response.Response([])

        item_ids = ",".join([str(x) for x in page_items])
        item_query = {
            "fq": ["type:item", "{!term f=pk}"+item_ids]
        }
        item_res = conn.search("*:*", **item_query)

        if not item_res.hits > 0:
            return response.Response([])

        annotation_list = []

        return response.Response({})
