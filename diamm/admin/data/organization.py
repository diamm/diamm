from django.contrib import admin
from diamm.models.data.organization import Organization
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from simple_history.admin import SimpleHistoryAdmin


@admin.register(Organization)
class OrganizationAdmin(SimpleHistoryAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('name',)

    related_search_fields = {
        'location': ('name', 'parent__name')
    }
