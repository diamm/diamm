from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.geographic_area import CITY, COUNTRY, STATE, REGION, FICTIONAL
from simple_history.admin import SimpleHistoryAdmin


class GeographicAreaTypeListFilter(admin.SimpleListFilter):
    title = _('Area Type')
    parameter_name = 'area_type'

    def lookups(self, request, model_admin):
        return (
            (CITY, _('City')),
            (COUNTRY, _('Country')),
            (STATE, _('County/Province/State/Canton')),
            (REGION, _('Region/Cultural area')),
            (FICTIONAL, _('Fictional/Imaginary'))
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(type=self.value())


@admin.register(GeographicArea)
class GeographicAreaAdmin(SimpleHistoryAdmin, ForeignKeyAutocompleteAdmin):
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
