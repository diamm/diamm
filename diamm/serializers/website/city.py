import ypres
from rest_framework.reverse import reverse


class CityProvenanceSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.MethodField()
    city_uncertain = ypres.BoolField()
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


class OrganizationSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()

    def get_url(self, obj) -> str:
        return reverse(
            "organization-detail",
            kwargs={"pk": obj.id},
            request=self.context["request"],
        )


class CountryCitySerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()

    def get_url(self, obj) -> str:
        return reverse(
            "country-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )


class ArchiveCitySerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()
    siglum = ypres.StrField()

    def get_url(self, obj) -> str:
        return reverse(
            "archive-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )


class CityListSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()

    def get_url(self, obj) -> str:
        return reverse(
            "city-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )


class CityDetailSerializer(ypres.Serializer):
    url = ypres.MethodField()
    pk = ypres.IntField()
    name = ypres.StrField()
    archives = ypres.MethodField()
    country = ypres.MethodField()
    # provenance_relationships = ypres.MethodField()
    organizations = ypres.MethodField()
    provenance = ypres.MethodField()
    variant_names = ypres.StrField(required=False)

    def get_archives(self, obj) -> list:
        return ArchiveCitySerializer(
            obj.archives.all(), many=True, context=self.context
        ).serialized_many

    def get_country(self, obj) -> dict:
        return CountryCitySerializer(obj.parent, context=self.context).serialized

    # def get_provenance_relationships(self, obj):
    #     return ProvenanceSerializer(obj.city_sources.all(), many=True, context=self.context).data

    def get_organizations(self, obj) -> list:
        return OrganizationSerializer(
            obj.organizations.all(), many=True, context=self.context
        ).serialized_many

    def get_provenance(self, obj) -> list:
        return CityProvenanceSerializer(
            obj.city_sources.all()
            .select_related("source__archive")
            .order_by("source__archive__name", "source__sort_order"),
            many=True,
            context=self.context,
        ).serialized_many

    def get_url(self, obj) -> str:
        return reverse(
            "city-detail", kwargs={"pk": obj.id}, request=self.context["request"]
        )
