from rest_framework import generics
from rest_framework import renderers
from rest_framework.response import Response
from diamm.models.data.geographic_area import GeographicArea
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.serializers.website.city import CityDetailSerializer, CityListSerializer
from diamm.helpers.object_pagination import ObjectPagination


class CityList(generics.ListAPIView):
    template_name = "website/city/city_list.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = CityListSerializer
    pagination_class = ObjectPagination
    queryset = GeographicArea.objects.filter(type=GeographicArea.CITY)

    def initial(self, request, *args, **kwargs):
        letter = request.GET.get('l', None)

        if letter:
            self.queryset = self.queryset.filter(name__istartswith=letter)

        super(CityList, self).initial(request, *args, **kwargs)


class CityDetail(generics.RetrieveAPIView):
    template_name = "website/city/city_detail.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = CityDetailSerializer
    queryset = GeographicArea.objects.filter(type=GeographicArea.CITY)
