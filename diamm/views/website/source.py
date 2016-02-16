from rest_framework import generics
from rest_framework import renderers
from rest_framework import permissions
from rest_framework import response
from drf_ujson.renderers import UJSONRenderer
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.models.data.source import Source
from diamm.models.data.source_note import SourceNote
from diamm.serializers.website.source import SourceListSerializer, SourceDetailSerializer
from diamm.helpers.solr_iiif_manifest import IIIFManifest


class SourceList(generics.ListCreateAPIView):
    template_name = "website/source/source_list.jinja2"
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Source.objects.all()

    # For serializing large lists, we only need the minimal serializer,
    # but for accepting new objects we will pass it through the full serializer.
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SourceListSerializer
        elif self.request.method == 'POST':
            return SourceDetailSerializer


class SourceDetail(generics.RetrieveUpdateAPIView):
    """
    """
    template_name = "website/source/source_detail.jinja2"
    serializer_class = SourceDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # Optimization for retrieving
        prefetch = ['inventory__composition__composers__composer__notes',
                    'inventory',
                    'notes',
                    'bibliography']
        queryset = Source.objects.all()
        queryset = queryset.select_related('archive__city__parent').prefetch_related(*prefetch)
        return queryset


class SourceManifest(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)

    def get(self, request, pk, *args, **kwargs):
        manifest = IIIFManifest(pk, request)
        return response.Response(manifest.get())
