from rest_framework import generics
from django.db.models import Q
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.models.data.geographic_area import GeographicArea
from diamm.serializers.website.country import CountryDetailSerializer
from diamm.renderers.html_renderer import HTMLRenderer


class CountryDetail(generics.RetrieveAPIView):
    template_name = "website/country/country_detail.jinja2"
    queryset = GeographicArea.objects.filter(Q(type=GeographicArea.COUNTRY))
    serializer_class = CountryDetailSerializer
    renderer_classes = (HTMLRenderer, UJSONRenderer)


class CountryList(generics.ListAPIView):
    template_name = "website/country/country_list.jinja2"
    queryset = GeographicArea.objects.filter(Q(type=GeographicArea.COUNTRY)).select_related('parent')
    serializer_class = CountryDetailSerializer
    renderer_classes = (HTMLRenderer, UJSONRenderer)
    pagination_class = None
