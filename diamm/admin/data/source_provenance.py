from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.source_provenance import SourceProvenance


@admin.register(SourceProvenance)
class SourceProvenanceAdmin(VersionAdmin):
    list_display = (
        "source",
        "earliest_year",
        "latest_year",
        "get_city",
        "get_region",
        "get_country",
        "country_uncertain",
    )
    search_fields = (
        "source__name",
        "source__shelfmark",
        "source__identifiers__identifier",
        "=source__id",
    )
    list_filter = (
        "country_uncertain",
        "city_uncertain",
        "entity_uncertain",
        "region_uncertain",
    )
    raw_id_fields = ("source", "city", "country", "region", "protectorate")

    @admin.display(description="City")
    def get_city(self, obj):
        return obj.city

    @admin.display(description="Country")
    def get_country(self, obj):
        return obj.country

    @admin.display(description="Region")
    def get_region(self, obj):
        return obj.region
