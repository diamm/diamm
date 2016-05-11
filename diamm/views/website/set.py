from rest_framework import generics
from rest_framework import renderers
from diamm.models.data.set import Set
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.serializers.website.set import SetDetailSerializer


class SetDetail(generics.RetrieveAPIView):
    template_name = "website/set/set_detail.jinja2"
    serializer_class = SetDetailSerializer
    queryset = Set.objects.all()
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
