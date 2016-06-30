from rest_framework import generics
from rest_framework import renderers
from diamm.models.data.geographic_area import GeographicArea
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.serializers.website.city import CityDetailSerializer, CityListSerializer
from diamm.helpers.object_pagination import Object_Pagination


class CityList(generics.ListAPIView):
    template_name = "website/city/city_list.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = CityListSerializer
    queryset = GeographicArea.objects.filter(type=GeographicArea.CITY)
    pagination_class = Object_Pagination

class CityDetail(generics.RetrieveAPIView):
    template_name = "website/city/city_detail.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = CityDetailSerializer
    queryset = GeographicArea.objects.filter(type=GeographicArea.CITY)
