import pysolr
from django.conf import settings
from rest_framework import generics
from rest_framework import status
from rest_framework import response
from drf_ujson.renderers import UJSONRenderer
from diamm.models.data.source import Source
from diamm.serializers.website.source import SourceListSerializer, SourceDetailSerializer
from diamm.serializers.iiif.manifest import SourceManifestSerializer, CanvasSerializer


class SourceList(generics.ListAPIView):
    template_name = "website/source/source_list.jinja2"
    queryset = Source.objects.all()

    # For serializing large lists, we only need the minimal serializer,
    # but for accepting new objects we will pass it through the full serializer.
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SourceListSerializer
        elif self.request.method == 'POST':
            return SourceDetailSerializer


class SourceDetail(generics.RetrieveAPIView):
    template_name = "website/source/source_detail.jinja2"
    serializer_class = SourceDetailSerializer

    def get_queryset(self):
        # Optimization for retrieving
        prefetch = ['notes', 'catalogue_entries']
        queryset = Source.objects.all()
        queryset = queryset.select_related('archive__city__parent').prefetch_related(*prefetch)
        return queryset


class SourceManifest(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)

    def get(self, request, pk, *args, **kwargs):
        conn = pysolr.Solr(settings.SOLR['SERVER'])
        res = conn.search("*:*",
                          fq=["type:source", "pk:{0}".format(pk)])

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

