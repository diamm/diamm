import ypres
from rest_framework.reverse import reverse



class RegionCitySerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()

    def get_url(self, obj) -> str:
        return reverse(
            "city-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )


class RegionOrganizationSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()

    def get_url(self, obj) -> str:
        return reverse(
            "organization-detail",
            kwargs={"pk": obj.id},
            request=self.context["request"],
        )


class RegionProvenanceSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.MethodField()
    region_uncertain = ypres.BoolField()
    earliest_year = ypres.IntField(required=False)
    latest_year = ypres.IntField(required=False)

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source.id},
            request=self.context["request"],
        )

    def get_name(self, obj) -> str:
        return f"{obj.source.display_name}"


class RegionDetailSerializer(ypres.Serializer):
    url = ypres.MethodField()
    pk = ypres.IntField()
    name = ypres.StrField()
    parent = ypres.StrField()
    organizations = ypres.MethodField()
    cities = ypres.MethodField()
    provenance = ypres.MethodField()

    def get_organizations(self, obj) -> list:
        return RegionOrganizationSerializer(
            obj.organizations.all(), many=True, context=self.context
        ).serialized_many

    def get_cities(self, obj) -> list:
        return RegionCitySerializer(
            obj.cities.select_related("parent"), many=True, context=self.context
        ).serialized_many

    def get_provenance(self, obj) -> list:
        return RegionProvenanceSerializer(
            obj.region_sources.select_related("source"), many=True, context=self.context
        ).serialized_many

    def get_url(self, obj) -> list:
        return reverse(
            "region-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )
