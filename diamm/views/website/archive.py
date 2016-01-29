from rest_framework import generics
from rest_framework import renderers
from diamm.models.data.archive import Archive
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.serializers.website.archive import ArchiveDetailSerializer, ArchiveListSerializer


class ArchiveList(generics.ListAPIView):
    template_name = "website/archive/archive_list.jinja2"
    serializer_class = ArchiveListSerializer
    queryset = Archive.objects.all()
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)


class ArchiveDetail(generics.RetrieveAPIView):
    template_name = "website/archive/archive_detail.jinja2"
    serializer_class = ArchiveDetailSerializer
    queryset = Archive.objects.all()
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
