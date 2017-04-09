from rest_framework import generics
from rest_framework import renderers
from diamm.models.data.geographic_area import GeographicArea
from diamm.serializers.website.country import CountryDetailSerializer
from diamm.renderers.html_renderer import HTMLRenderer


class CountryDetail(generics.RetrieveAPIView):
    template_name = "website/country/country_detail.jinja2"
    queryset = GeographicArea.objects.filter(type=GeographicArea.COUNTRY)
    serializer_class = CountryDetailSerializer
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
