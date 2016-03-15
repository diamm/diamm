from django.contrib import admin
from diamm.models.data.organization import Organization
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin


@admin.register(Organization)
class OrganizationAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('name', 'location', 'type')
    list_filter = ('type',)
    search_fields = ('name',)

    related_search_fields = {
        'location': ('name', 'parent__name')
    }
