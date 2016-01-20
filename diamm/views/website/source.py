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
        return Source.objects.all().select_related('archive').prefetch_related('inventory')
