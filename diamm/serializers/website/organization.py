
import serpy
from django.contrib.contenttypes.prefetch import GenericPrefetch
from rest_framework.reverse import reverse

from diamm.models import Organization, Person
from diamm.models.data.geographic_area import GeographicArea
from diamm.serializers.serializers import ContextSerializer


class OrganizationLocationSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField(attr="name")
    parent = serpy.StrField(attr="parent")

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


class OrganizationSourceProvenanceSerializer(ContextSerializer):
    url = serpy.MethodField()
    source = serpy.StrField(attr="source.display_name")
    entity_uncertain = serpy.BoolField(attr="entity_uncertain")
    city = serpy.StrField(attr="city.name", required=False)
    country = serpy.StrField(attr="country.name", required=False)
    region = serpy.StrField(attr="region.name", required=False)
    protectorate = serpy.StrField(attr="protectorate.name", required=False)
    country_uncertain = serpy.BoolField(attr="country_uncertain")
    city_uncertain = serpy.BoolField(attr="city_uncertain")
    region_uncertain = serpy.BoolField(attr="region_uncertain")

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source_id},
            request=self.context["request"],
        )


class OrganizationSourceCopyistSerializer(ContextSerializer):
    url = serpy.MethodField()
    has_images = serpy.BoolField(attr="source.pages.exists", call=True, required=False)
    copyist_type = serpy.StrField(attr="copyist_type")
    uncertain = serpy.BoolField(attr="uncertain")
    source = serpy.StrField(attr="source.display_name")
    public_images = serpy.BoolField(attr="source.public_images", required=False)

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source_id},
            request=self.context["request"],
        )


class OrganizationSourceRelationshipSerializer(ContextSerializer):
    url = serpy.MethodField()
    relationship = serpy.StrField(attr="relationship_type")
    uncertain = serpy.BoolField(attr="uncertain")
    source = serpy.StrField(attr="source.display_name")
    has_images = serpy.BoolField(attr="source.pages.exists", call=True, required=False)
    public_images = serpy.BoolField(attr="source.public_images", required=False)

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source_id},
            request=self.context["request"],
        )


class OrganizationDetailSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    name = serpy.StrField()
    organization_type = serpy.StrField(attr="type.name")
    type = serpy.MethodField()
    related_sources = serpy.MethodField()
    copied_sources = serpy.MethodField()
    source_provenance = serpy.MethodField()
    location = serpy.MethodField()

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
            ).data
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
        ).data

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
        ).data

    def get_source_provenance(self, obj) -> list:
        return OrganizationSourceProvenanceSerializer(
            obj.sources_provenance.select_related(
                "source__archive__city", "city"
            ).all(),
            many=True,
            context={"request": self.context["request"]},
        ).data
