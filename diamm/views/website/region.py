from django.db.models import Q
from rest_framework import generics

from diamm.models.data.geographic_area import AreaTypeChoices, GeographicArea
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.region import RegionDetailSerializer


class RegionDetail(generics.RetrieveAPIView):
    template_name = "website/region/region_detail.jinja2"
    queryset = GeographicArea.objects.filter(
        Q(type=AreaTypeChoices.REGION) | Q(type=AreaTypeChoices.STATE)
    )
    serializer_class = RegionDetailSerializer
    renderer_classes = (HTMLRenderer, UJSONRenderer)
