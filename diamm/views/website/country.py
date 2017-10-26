from rest_framework import generics
from rest_framework import renderers
from django.db.models import Q
from diamm.models.data.geographic_area import GeographicArea
from diamm.serializers.website.country import CountryDetailSerializer
from diamm.renderers.html_renderer import HTMLRenderer


class CountryDetail(generics.RetrieveAPIView):
    template_name = "website/country/country_detail.jinja2"
    queryset = GeographicArea.objects.filter(Q(type=GeographicArea.COUNTRY))
    serializer_class = CountryDetailSerializer
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)


class CountryList(generics.ListAPIView):
    template_name = "website/country/country_list.jinja2"
    queryset = GeographicArea.objects.filter(Q(type=GeographicArea.COUNTRY) | Q(parent_id=10)).select_related('parent')
    serializer_class = CountryDetailSerializer
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    pagination_class = None
