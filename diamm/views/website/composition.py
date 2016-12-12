from rest_framework import generics
from rest_framework import renderers
from diamm.models.data.composition import Composition
from diamm.serializers.website.composition import CompositionDetailSerializer
from diamm.renderers.html_renderer import HTMLRenderer


class CompositionDetail(generics.RetrieveAPIView):
    template_name = "website/composition/composition_detail.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = CompositionDetailSerializer
    queryset = Composition.objects.all()






