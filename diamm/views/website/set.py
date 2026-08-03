from rest_framework import generics

from diamm.models.data.set import Set
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONLDRenderer, UJSONRenderer
from diamm.serializers.iiif.collection import SetCollectionSerializer
from diamm.serializers.set_sync import SetSyncSerializer
from diamm.serializers.website.set import SetDetailSerializer


class SetDetail(generics.RetrieveAPIView):
    template_name = "website/set/set_detail.jinja2"
    serializer_class = SetDetailSerializer
    renderer_classes = (HTMLRenderer, UJSONRenderer)
    queryset = Set.objects.all()


class SetCollectionDetail(generics.RetrieveAPIView):
    serializer_class = SetCollectionSerializer
    renderer_classes = (UJSONLDRenderer,)
    queryset = Set.objects.all()


class SetSyncDetail(generics.RetrieveAPIView):
    serializer_class = SetSyncSerializer
    renderer_classes = (UJSONRenderer,)
    queryset = Set.objects.all()
