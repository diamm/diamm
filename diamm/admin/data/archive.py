from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin

from diamm.admin.helpers.html import admin_change_link
from diamm.models.data.archive import Archive
from diamm.models.data.archive_identifier import ArchiveIdentifier
from diamm.models.data.archive_note import ArchiveNote
from diamm.models.data.geographic_area import AreaTypeChoices, GeographicArea


class ArchiveNoteInline(admin.TabularInline):
    model = ArchiveNote
    extra = 0

    formfield_overrides = {models.TextField: {"widget": AdminPagedownWidget}}


class CountryListFilter(admin.SimpleListFilter):
    title = _("Country or State")
    parameter_name = "country"

    def lookups(self, request, model_admin):
        countries = GeographicArea.objects.filter(
            Q(type=AreaTypeChoices.COUNTRY) | Q(type=AreaTypeChoices.STATE)
        )
        return [(c.pk, c.name) for c in countries]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(city__parent__pk=self.value())


class ArchiveIdentifierInline(admin.TabularInline):
    verbose_name = "Identifier"
    model = ArchiveIdentifier
    extra = 0
    readonly_fields = ("get_external_url",)

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return admin_change_link(instance.identifier_url, instance.identifier_url)


@admin.register(Archive)
class ArchiveAdmin(VersionAdmin):
    save_on_top = True
    list_display = ("name", "get_city", "get_country", "siglum", "updated")
    search_fields = (
        "name",
        "siglum",
        "former_sigla",
        "city__name",
        "city__parent__name",
    )
    list_filter = (CountryListFilter,)
    inlines = (ArchiveNoteInline, ArchiveIdentifierInline)
    raw_id_fields = ("city",)
    view_on_site = True
    readonly_fields = ("created", "updated")

    @admin.display(description="City", ordering="city__name")
    def get_city(self, obj):
        return obj.city.name if obj.city else "-"

    @admin.display(description="Country", ordering="city__parent__name")
    def get_country(self, obj):
        if obj.city and obj.city.parent:
            return obj.city.parent.name
        return "-"

    def get_queryset(self, request):
        qset = super().get_queryset(request)
        qset = qset.select_related("city__parent")
        return qset
