from rest_framework import generics

from diamm.models.data.composition import Composition
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.composition import CompositionDetailSerializer


class CompositionDetail(generics.RetrieveAPIView):
    template_name = "website/composition/composition_detail.jinja2"
    renderer_classes = (HTMLRenderer, UJSONRenderer)
    serializer_class = CompositionDetailSerializer
    queryset = Composition.objects.all().prefetch_related(
        "sources__voices", "sources__pages"
    )
