from django.contrib import admin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from dynamic_raw_id.admin import DynamicRawIDMixin
from reversion.admin import VersionAdmin

from diamm.models.data.archive import Archive
from diamm.models.data.archive_identifier import ArchiveIdentifier
from diamm.models.data.archive_note import ArchiveNote
from diamm.models.data.geographic_area import GeographicArea


class ArchiveNoteInline(admin.TabularInline):
    model = ArchiveNote
    extra = 0


class CountryListFilter(admin.SimpleListFilter):
    title = _('Country or State')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries = GeographicArea.objects.filter(Q(type=GeographicArea.COUNTRY) | Q(type=GeographicArea.STATE))
        return [(c.pk, c.name) for c in countries]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(city__parent__pk=self.value())


class ArchiveIdentifierInline(admin.TabularInline):
    verbose_name = "Identifier"
    model = ArchiveIdentifier
    extra = 0


@admin.register(Archive)
class ArchiveAdmin(DynamicRawIDMixin, VersionAdmin):
    save_on_top = True
    list_display = ('name', 'get_city', 'get_country', 'siglum', 'updated')
    search_fields = ('name', 'siglum', 'former_sigla', 'city__name', 'city__parent__name')
    list_filter = (CountryListFilter,)
    inlines = (ArchiveNoteInline, ArchiveIdentifierInline)
    dynamic_raw_id_fields = ('city',)
    view_on_site = True
    readonly_fields = ("created", "updated")

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
