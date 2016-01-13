from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from diamm.models.data.geographic_area import GeographicArea
from reversion.admin import VersionAdmin


class GeographicAreaTypeListFilter(admin.SimpleListFilter):
    title = _('Area Type')
    parameter_name = 'area_type'

    def lookups(self, request, model_admin):
        return (
            (GeographicArea.CITY, _('City')),
            (GeographicArea.COUNTRY, _('Country')),
            (GeographicArea.STATE, _('County/Province/State/Canton')),
            (GeographicArea.REGION, _('Region/Cultural area')),
            (GeographicArea.FICTIONAL, _('Fictional/Imaginary'))
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(type=self.value())


@admin.register(GeographicArea)
class GeographicAreaAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('name', 'area_type', 'get_parent')
    search_fields = ('name',)
    list_filter = (GeographicAreaTypeListFilter,)

    related_search_fields = {
        'parent': ('name',)
    }

    def get_parent(self, obj):
        if obj.parent:
            return "{0}".format(obj.parent.name)
        return None
    get_parent.short_description = "Parent"
