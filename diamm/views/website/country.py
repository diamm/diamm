from rest_framework import generics
from rest_framework import renderers
from diamm.models.data.geographic_area import GeographicArea
from diamm.serializers.website.country import CountryListSerializer, CountryDetailSerializer
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.helpers.object_pagination import ObjectPagination


class CountryList(generics.ListAPIView):
    template_name = "website/country/country_list.jinja2"
    queryset = GeographicArea.objects.filter(type=GeographicArea.COUNTRY)
    serializer_class = CountryListSerializer
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    pagination_class = ObjectPagination

    def initial(self, request, *args, **kwargs):
        letter = request.GET.get('l', None)

        if letter:
            self.queryset = self.queryset.filter(name__istartswith=letter)

        super(CountryList, self).initial(request, args, kwargs)


class CountryDetail(generics.RetrieveAPIView):
    template_name = "website/country/country_detail.jinja2"
    queryset = GeographicArea.objects.filter(type=GeographicArea.COUNTRY)
    serializer_class = CountryDetailSerializer
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
