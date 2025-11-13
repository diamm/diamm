from rest_framework import generics

from diamm.helpers.object_pagination import ObjectPagination
from diamm.models.data.geographic_area import AreaTypeChoices, GeographicArea
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.city import CityDetailSerializer, CityListSerializer


class CityList(generics.ListAPIView):
    template_name = "website/city/city_list.jinja2"
    renderer_classes = (HTMLRenderer, UJSONRenderer)
    serializer_class = CityListSerializer
    pagination_class = ObjectPagination
    queryset = GeographicArea.objects.filter(type=AreaTypeChoices.CITY)

    def initial(self, request, *args, **kwargs):
        letter = request.GET.get("l", None)

        if letter:
            self.queryset = self.queryset.filter(name__istartswith=letter)

        super().initial(request, *args, **kwargs)


class CityDetail(generics.RetrieveAPIView):
    template_name = "website/city/city_detail.jinja2"
    renderer_classes = (HTMLRenderer, UJSONRenderer)
    serializer_class = CityDetailSerializer
    queryset = GeographicArea.objects.filter(type=AreaTypeChoices.CITY)
