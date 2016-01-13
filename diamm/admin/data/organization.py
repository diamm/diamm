from django.contrib import admin
from diamm.models.data.organization import Organization
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin


@admin.register(Organization)
class OrganizationAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('name', 'location', 'type')

    related_search_fields = {
        'location': ('name', 'parent__name')
    }
