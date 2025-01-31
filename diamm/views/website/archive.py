from rest_framework import generics

from diamm.models.data.archive import Archive
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.archive import ArchiveDetailSerializer


class ArchiveDetail(generics.RetrieveAPIView):
    template_name = "website/archive/archive_detail.jinja2"
    serializer_class = ArchiveDetailSerializer
    queryset = Archive.objects.prefetch_related(
        "sources__archive__city", "notes", "identifiers"
    ).all()
    renderer_classes = (HTMLRenderer, UJSONRenderer)
