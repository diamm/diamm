from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from diamm.models.data.geographic_area import GeographicArea
from reversion.admin import VersionAdmin


@admin.register(GeographicArea)
class GeographicAreaAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('name', 'area_type', 'get_parent')
    search_fields = ('name',)
    list_filter = ('type',)

    related_search_fields = {
        'parent': ('name',)
    }

    def get_parent(self, obj):
        if obj.parent:
            return "{0}".format(obj.parent.name)
        return None
    get_parent.short_description = "Parent"
