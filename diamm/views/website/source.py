import pysolr
from django.conf import settings
from rest_framework import generics
from rest_framework import status
from rest_framework import response
from drf_ujson.renderers import UJSONRenderer
from diamm.models.data.source import Source
from diamm.serializers.website.source import SourceDetailSerializer
from diamm.serializers.iiif.manifest import SourceManifestSerializer
from diamm.serializers.iiif.canvas import CanvasSerializer
from diamm.serializers.iiif.service import ServiceSerializer


class SourceDetail(generics.RetrieveAPIView):
    template_name = "website/source/source_detail.jinja2"
    serializer_class = SourceDetailSerializer

    def get_queryset(self):
        # Optimization for retrieving
        queryset = Source.objects.all()
        queryset = queryset.select_related('archive__city__parent')
        return queryset

    def get(self, request, *args, **kwargs):
        if request.accepted_renderer.format == "html":
            source_name = Source.objects.get(id=kwargs['pk']).display_name
            return response.Response({'pk': kwargs['pk'], 'display_name': source_name})
        return super(SourceDetail, self).get(request, args, kwargs)


class SourceManifest(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)

    def get(self, request, pk, *args, **kwargs):
        conn = pysolr.Solr(settings.SOLR['SERVER'])
        res = conn.search("*:*",
                          fq=["type:source", "pk:{0}".format(pk), 'public_images_b:true'],
                          rows=1)

        if res.hits == 0:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

        manifest = SourceManifestSerializer(res.docs[0],
                                            context={"request": request})
        return response.Response(manifest.data)


class SourceCanvasDetail(generics.GenericAPIView):
    """
        The view handler for the IIIF Canvas resolver. Uses Solr to
         retrieve pre-indexed results for the contents of a page.
    """
    renderer_classes = (UJSONRenderer,)

    def get(self, request, source_id, page_id):
        page_fields = [
            "id",
            "pk",
            "source_i",
            "numeration_s",
            "[child parentFilter=type:page childFilter=type:image]"
        ]

        conn = pysolr.Solr(settings.SOLR['SERVER'])
        res = conn.search("*:*",
                          fq=["type:page", "pk:{0}".format(page_id)],
                          fl=page_fields)
        canvas = CanvasSerializer(res.docs[0], context={"request": request})

        return response.Response(canvas.data)


class SourceRangeDetail(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)


class SourceItemDetail(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)

    def get(self, request, source_id, item_id):
        conn = pysolr.Solr(settings.SOLR['SERVER'])

        # The pages_ii:[* TO *] query ensures we retrieve only
        # those records that have images associated with them.
        structure_query = {
            "fq": ["type:item",
                   "pk:{0}".format(item_id),
                   "source_i:{0}".format(source_id),
                   "pages_ii:[* TO *]"],
            "sort": "folio_start_ans asc",
            "rows": 10000,
        }
        structure_res = conn.search("*:*", **structure_query)
        structures = ServiceSerializer(structure_res.docs[0],
                                       context={"request": request}).data

        return response.Response(structures)



