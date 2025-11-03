import ypres
from rest_framework.reverse import reverse

from diamm.models.data.geographic_area import GeographicArea, AreaTypeChoices


class CountryStateSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()

    def get_url(self, obj):
        return reverse(
            "region-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )


class CountryRegionSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()

    def get_url(self, obj):
        return reverse(
            "region-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )


class CountryCitySerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()

    def get_url(self, obj):
        return reverse(
            "city-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )


class CountryListSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()
    cities = ypres.MethodField()
    regions = ypres.MethodField()
    states = ypres.MethodField()

    # If the list is prefetched, it's already an in-memory list of instances.
    # Fall back to properties only if not prefetched (e.g., for tests).
    def _get_list(self, obj, attr_name, fallback_qs):
        items = getattr(obj, attr_name, None)
        return items if items is not None else list(fallback_qs)

    def get_cities(self, obj):
        items = self._get_list(obj, "prefetched_cities", obj.cities.order_by("name"))
        return CountryCitySerializer(
            items, many=True, context=self.context
        ).serialized_many

    def get_regions(self, obj):
        items = self._get_list(obj, "prefetched_regions", obj.regions.order_by("name"))
        return CountryRegionSerializer(
            items, many=True, context=self.context
        ).serialized_many

    def get_states(self, obj):
        items = self._get_list(obj, "prefetched_states", obj.states.order_by("name"))
        return CountryStateSerializer(
            items, many=True, context=self.context
        ).serialized_many

    def get_url(self, obj):
        return reverse(
            "country-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )


class CountryDetailSerializer(ypres.Serializer):
    url = ypres.MethodField()
    pk = ypres.IntField()
    name = ypres.StrField()
    cities = ypres.MethodField()
    regions = ypres.MethodField()
    states = ypres.MethodField()
    provenance_relationships = ypres.MethodField()

    def get_cities(self, obj):
        return CountryCitySerializer(
            obj.cities.select_related("parent").order_by("name"),
            many=True,
            context=self.context,
        ).serialized_many

    def get_regions(self, obj):
        return CountryRegionSerializer(
            obj.regions.select_related("parent").order_by("name"),
            many=True,
            context=self.context,
        ).serialized_many

    def get_states(self, obj):
        return CountryStateSerializer(
            obj.states.select_related("parent").order_by("name"),
            many=True,
            context=self.context,
        ).serialized_many

    def get_url(self, obj):
        if obj.type in (AreaTypeChoices.STATE, AreaTypeChoices.REGION):
            return reverse(
                "region-detail", kwargs={"pk": obj.id}, request=self.context["request"]
            )
        elif obj.type == AreaTypeChoices.CITY:
            return reverse(
                "city-detail", kwargs={"pk": obj.id}, request=self.context["request"]
            )
        elif obj.type == AreaTypeChoices.COUNTRY:
            return reverse(
                "country-detail", kwargs={"pk": obj.id}, request=self.context["request"]
            )
        else:
            # return a URL that does not link anywhere.
            return "#"

    def get_provenance_relationships(self, obj):
        pass
