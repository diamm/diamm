
import ypres
from django.contrib.contenttypes.prefetch import GenericPrefetch
from rest_framework.reverse import reverse

from diamm.models import Organization, Person
from diamm.models.data.geographic_area import GeographicArea


class OrganizationLocationSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField(attr="name")
    parent = ypres.StrField(attr="parent")

    def get_url(self, obj) -> str | None:
        view_type: str
        if obj.type == GeographicArea.CITY:
            view_type = "city-detail"
        elif obj.type == GeographicArea.COUNTRY:
            view_type = "country-detail"
        else:
            return None

        return reverse(
            view_type, kwargs={"pk": obj.pk}, request=self.context["request"]
        )


class OrganizationSourceProvenanceSerializer(ypres.Serializer):
    url = ypres.MethodField()
    source = ypres.StrField(attr="source.display_name")
    entity_uncertain = ypres.BoolField(attr="entity_uncertain")
    city = ypres.StrField(attr="city.name", required=False)
    country = ypres.StrField(attr="country.name", required=False)
    region = ypres.StrField(attr="region.name", required=False)
    protectorate = ypres.StrField(attr="protectorate.name", required=False)
    country_uncertain = ypres.BoolField(attr="country_uncertain")
    city_uncertain = ypres.BoolField(attr="city_uncertain")
    region_uncertain = ypres.BoolField(attr="region_uncertain")

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source_id},
            request=self.context["request"],
        )


class OrganizationSourceCopyistSerializer(ypres.Serializer):
    url = ypres.MethodField()
    has_images = ypres.BoolField(attr="source.pages.exists", call=True, required=False)
    copyist_type = ypres.StrField(attr="copyist_type")
    uncertain = ypres.BoolField(attr="uncertain")
    source = ypres.StrField(attr="source.display_name")
    public_images = ypres.BoolField(attr="source.public_images", required=False)

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source_id},
            request=self.context["request"],
        )


class OrganizationSourceRelationshipSerializer(ypres.Serializer):
    url = ypres.MethodField()
    relationship = ypres.StrField(attr="relationship_type")
    uncertain = ypres.BoolField(attr="uncertain")
    source = ypres.StrField(attr="source.display_name")
    has_images = ypres.BoolField(attr="source.pages.exists", call=True, required=False)
    public_images = ypres.BoolField(attr="source.public_images", required=False)

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source_id},
            request=self.context["request"],
        )


class OrganizationDetailSerializer(ypres.Serializer):
    pk = ypres.IntField()
    url = ypres.MethodField()
    name = ypres.StrField()
    organization_type = ypres.StrField(attr="type.name")
    type = ypres.MethodField()
    related_sources = ypres.MethodField()
    copied_sources = ypres.MethodField()
    source_provenance = ypres.MethodField()
    location = ypres.MethodField()

    def get_url(self, obj) -> str:
        return reverse(
            "organization-detail",
            kwargs={"pk": obj.pk},
            request=self.context["request"],
        )

    def get_location(self, obj):
        if obj.location:
            return OrganizationLocationSerializer(
                obj.location, context={"request": self.context["request"]}
            ).serialized
        return None

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_related_sources(self, obj) -> list:
        return OrganizationSourceRelationshipSerializer(
            obj.sources_related.select_related(
                "relationship_type", "source__archive__city"
            )
            .prefetch_related(
                GenericPrefetch(
                    "related_entity", [Person.objects.all(), Organization.objects.all()]
                ),
                "source__pages__images",
                "source__inventory",
            )
            .all(),
            context={"request": self.context["request"]},
            many=True,
        ).serialized_many

    def get_copied_sources(self, obj) -> list:
        return OrganizationSourceCopyistSerializer(
            obj.sources_copied.select_related("source__archive__city")
            .prefetch_related(
                GenericPrefetch(
                    "copyist",
                    [
                        Person.objects.prefetch_related("identifiers", "roles").all(),
                        Organization.objects.prefetch_related("identifiers").all(),
                    ],
                ),
                "source__pages__images",
                "source__inventory",
            )
            .all(),
            context={"request": self.context["request"]},
            many=True,
        ).serialized_many

    def get_source_provenance(self, obj) -> list:
        return OrganizationSourceProvenanceSerializer(
            obj.sources_provenance.select_related(
                "source__archive__city", "city"
            ).all(),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many
