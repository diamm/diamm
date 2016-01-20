from rest_framework import generics
from rest_framework import renderers
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.models.data.source import Source
from diamm.serializers.website.source import SourceListSerializer, SourceDetailSerializer


class SourceList(generics.ListAPIView):
    template_name = "website/source/source_list.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = SourceListSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Source.objects.all()
        else:
            return Source.objects.filter(public=True)


class SourceDetail(generics.RetrieveAPIView):
    """
        This is the description.
    """
    template_name = "website/source/source_detail.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = SourceDetailSerializer

    def get_queryset(self):
        # Optimization for retrieving
        prefetch = ['inventory__composition__composers__composer__notes', 'inventory__notes']
        queryset = Source.objects.all()
        queryset = queryset.select_related('archive__city__parent').prefetch_related(*prefetch)
        return queryset
