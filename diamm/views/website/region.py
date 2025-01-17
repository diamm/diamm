from django.db.models import Q
from rest_framework import generics

from diamm.models.data.geographic_area import GeographicArea
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.region import RegionDetailSerializer


class RegionDetail(generics.RetrieveAPIView):
    template_name = "website/region/region_detail.jinja2"
    queryset = GeographicArea.objects.filter(
        Q(type=GeographicArea.REGION) | Q(type=GeographicArea.STATE)
    )
    serializer_class = RegionDetailSerializer
    renderer_classes = (HTMLRenderer, UJSONRenderer)
