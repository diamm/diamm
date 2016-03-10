from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from diamm.models.data.source_provenance import SourceProvenance
from reversion.admin import VersionAdmin


@admin.register(SourceProvenance)
class SourceProvenanceAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('source', 'earliest_year', 'latest_year', 'country_uncertain')
    search_fields = ('source__name', 'source__identifiers__identifier')
    list_filter = ('country_uncertain', 'city_uncertain', 'entity_uncertain', 'region_uncertain')

    related_search_fields = {
        'source': ('name', 'identifiers__name'),
        'organization': ('name',),
        'city': ('name',),
        'country': ('name',),
        'region': ('name',),
        'protectorate': ('name',)
    }
