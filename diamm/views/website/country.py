from django.db.models import Exists, OuterRef, Prefetch, Q
from rest_framework import generics

from diamm.models.data.geographic_area import AreaTypeChoices, GeographicArea
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.country import (
    CountryDetailSerializer,
    CountryListSerializer,
)


class CountryDetail(generics.RetrieveAPIView):
    template_name = "website/country/country_detail.jinja2"
    queryset = GeographicArea.objects.filter(Q(type=AreaTypeChoices.COUNTRY))
    serializer_class = CountryDetailSerializer
    renderer_classes = (HTMLRenderer, UJSONRenderer)


Country = GeographicArea
Child = GeographicArea


class CountryList(generics.ListAPIView):
    template_name = "website/country/country_list.jinja2"
    queryset = (
        Country.objects.filter(type=AreaTypeChoices.COUNTRY)
        .annotate(
            has_children=Exists(
                Child.objects.filter(
                    parent=OuterRef("pk"),
                    type__in=[
                        AreaTypeChoices.CITY,
                        AreaTypeChoices.REGION,
                        AreaTypeChoices.STATE,
                    ],
                )
            )
        )
        .filter(has_children=True)
        .only("id", "name", "type")  # keep base lean
        .prefetch_related(
            # Cities
            Prefetch(
                "geographicarea_set",
                queryset=Child.objects.filter(type=AreaTypeChoices.CITY)
                .select_related("parent")  # pull each city's parent (the country)
                .only("id", "name", "type", "parent_id", "parent__id", "parent__name")
                .order_by("name"),
                to_attr="prefetched_cities",
            ),
            # Regions
            Prefetch(
                "geographicarea_set",
                queryset=Child.objects.filter(type=AreaTypeChoices.REGION)
                .select_related("parent")
                .only("id", "name", "type", "parent_id", "parent__id", "parent__name")
                .order_by("name"),
                to_attr="prefetched_regions",
            ),
            # States
            Prefetch(
                "geographicarea_set",
                queryset=Child.objects.filter(type=AreaTypeChoices.STATE)
                .select_related("parent")
                .only("id", "name", "type", "parent_id", "parent__id", "parent__name")
                .order_by("name"),
                to_attr="prefetched_states",
            ),
            # If you render these too:
            "legacy_id",
            # archives / organizations if they are reverse relations:
            # "archives",
            # "organizations",
        )
    )
    serializer_class = CountryListSerializer
    renderer_classes = (HTMLRenderer, UJSONRenderer)
    pagination_class = None
