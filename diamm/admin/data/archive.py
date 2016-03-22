from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from diamm.models.data.archive import Archive
from diamm.models.data.archive_note import ArchiveNote
from diamm.models.data.geographic_area import GeographicArea
from reversion.admin import VersionAdmin
from django.utils.translation import ugettext_lazy as _


class ArchiveNoteInline(admin.TabularInline):
    model = ArchiveNote
    extra = 0


class CountryListFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries = GeographicArea.objects.filter(type=GeographicArea.COUNTRY)
        return [(c.pk, c.name) for c in countries]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(city__parent__pk=self.value())


@admin.register(Archive)
class ArchiveAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('name', 'get_city', 'get_country', 'siglum',)
    search_fields = ('name', 'siglum', 'city__name', 'city__parent__name')
    list_filter = (CountryListFilter,)
    inlines = (ArchiveNoteInline,)

    def get_city(self, obj):
        return "{0}".format(obj.city.name)
    get_city.short_description = "City"
    get_city.admin_order_field = "city__name"

    def get_country(self, obj):
        return "{0}".format(obj.city.parent.name)
    get_country.short_description = "Country"
    get_country.admin_order_field = "city__parent__name"

    def get_queryset(self, request):
        qset = super(ArchiveAdmin, self).get_queryset(request)
        qset = qset.select_related('city__parent')
        return qset
