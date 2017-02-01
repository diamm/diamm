from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from diamm.models.data.source_provenance import SourceProvenance
from reversion.admin import VersionAdmin


@admin.register(SourceProvenance)
class SourceProvenanceAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('source', 'earliest_year', 'latest_year', 'get_city', 'get_region', 'get_country', 'country_uncertain')
    search_fields = ('source__name', 'source__shelfmark', 'source__identifiers__identifier')
    list_filter = ('country_uncertain', 'city_uncertain', 'entity_uncertain', 'region_uncertain')

    related_search_fields = {
        'source': ('name', 'identifiers__name'),
        'organization': ('name',),
        'city': ('name',),
        'country': ('name',),
        'region': ('name',),
        'protectorate': ('name',)
    }

    def get_city(self, obj):
        return obj.city
    get_city.short_description = "city"

    def get_country(self, obj):
        return obj.country
    get_country.short_description = "country"

    def get_region(self, obj):
        return obj.region
    get_region.short_description = "region"
