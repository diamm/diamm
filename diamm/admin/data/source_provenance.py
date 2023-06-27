from django.contrib import admin
from dynamic_raw_id.admin import DynamicRawIDMixin
from reversion.admin import VersionAdmin

from diamm.models.data.source_provenance import SourceProvenance


@admin.register(SourceProvenance)
class SourceProvenanceAdmin(DynamicRawIDMixin, VersionAdmin):
    list_display = ('source', 'earliest_year', 'latest_year', 'get_city', 'get_region', 'get_country', 'country_uncertain')
    search_fields = ('source__name', 'source__shelfmark', 'source__identifiers__identifier', '=source__id')
    list_filter = ('country_uncertain', 'city_uncertain', 'entity_uncertain', 'region_uncertain')
    dynamic_raw_id_fields = ("source", "organization", "city", "country", "region", "protectorate")

    def get_city(self, obj):
        return obj.city
    get_city.short_description = "city"

    def get_country(self, obj):
        return obj.country
    get_country.short_description = "country"

    def get_region(self, obj):
        return obj.region
    get_region.short_description = "region"
