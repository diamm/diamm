import ypres
from rest_framework.reverse import reverse

from diamm.models.data.geographic_area import GeographicArea


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
        if obj.type in (GeographicArea.STATE, GeographicArea.REGION):
            return reverse(
                "region-detail", kwargs={"pk": obj.id}, request=self.context["request"]
            )
        elif obj.type == GeographicArea.CITY:
            return reverse(
                "city-detail", kwargs={"pk": obj.id}, request=self.context["request"]
            )
        elif obj.type == GeographicArea.COUNTRY:
            return reverse(
                "country-detail", kwargs={"pk": obj.id}, request=self.context["request"]
            )
        else:
            # return a URL that does not link anywhere.
            return "#"

    def get_provenance_relationships(self, obj):
        pass
