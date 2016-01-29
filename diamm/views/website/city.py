from rest_framework import generics
from rest_framework import renderers
from diamm.models.data.geographic_area import GeographicArea
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.serializers.website.city import CityDetailSerializer, CityListSerializer


class CityList(generics.ListAPIView):
    template_name = "website/city/city_list.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = CityListSerializer
    queryset = GeographicArea.objects.filter(type=GeographicArea.CITY)


class CityDetail(generics.RetrieveAPIView):
    template_name = "website/city/city_detail.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = CityDetailSerializer
    queryset = GeographicArea.objects.filter(type=GeographicArea.CITY)
