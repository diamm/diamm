from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms import TextInput, Textarea
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin
from pagedown.widgets import AdminPagedownWidget
from salmonella.admin import SalmonellaMixin
from rest_framework.reverse import reverse
from diamm.models.data.item import Item
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.source import Source
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_url import SourceURL
from diamm.models.data.source_bibliography import SourceBibliography
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.page import Page


class SourceRelationshipInline(SalmonellaMixin, admin.StackedInline):
    model = SourceRelationship
    extra = 0


class BibliographyInline(SalmonellaMixin, admin.TabularInline):
    model = SourceBibliography
    verbose_name_plural = "Bibliography Entries"
    verbose_name = "Bibliography Entry"
    extra = 0
    salmonella_fields = ('bibliography',)
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '160'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40})}
    }


class IdentifiersInline(admin.TabularInline):
    model = SourceIdentifier
    extra = 0


class NotesInline(admin.TabularInline):
    model = SourceNote
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }


class PagesInline(admin.TabularInline):
    model = Page
    extra = 0
    classes = ('collapse',)


class URLsInline(admin.TabularInline):
    model = SourceURL
    extra = 0


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    classes = ('collapse',)
    # salmonella_fields = ('composition', 'pages')
    fields = ('id', 'composition', 'get_composers', 'source_order',)
    readonly_fields = ('id', 'composition', 'get_composers')

    def get_composers(self, obj):
        if obj.composition:
            return "{0}".format(obj.composition.composer_names)


class InventoryFilter(admin.SimpleListFilter):
    title = _('Inventory')
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Source has inventory")),
            ("no", _("Source does not have inventory"))
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        val = self.value()
        if val == "yes":
            return queryset.filter(inventory__isnull=False).distinct()
        elif val == "no":
            return queryset.filter(inventory__isnull=True).distinct()


class CountryListFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries = GeographicArea.objects.filter(Q(type=GeographicArea.COUNTRY) | Q(type=GeographicArea.STATE))
        return [(c.pk, c.name) for c in countries]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(archive__city__parent__pk=self.value())


@admin.register(Source)
class SourceAdmin(SalmonellaMixin, VersionAdmin):
    save_on_top = True
    list_display = ('shelfmark',
                    'name',
                    'get_city',
                    'get_archive',
                    'public',
                    'public_images',
                    'inventory_provided',
                    'sort_order')
    search_fields = ('identifiers__identifier',
                     'name', 'archive__name',
                     'archive__siglum', 'archive__city__name', 'shelfmark',
                     "=pk")
    inlines = (IdentifiersInline, NotesInline, URLsInline,
               BibliographyInline, SourceRelationshipInline, PagesInline, ItemInline)
    list_filter = (CountryListFilter, InventoryFilter)
    list_editable = ('sort_order',)
    filter_horizontal = ['notations']
    # actions = (sort_sources,)
    salmonella_fields = ('cover_image', 'archive')

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }

    def get_city(self, obj):
        return "{0} ({1})".format(obj.archive.city.name, obj.archive.city.parent.name)
    get_city.short_description = "City"

    def get_archive(self, obj):
        return "{0}".format(obj.archive.name)
    get_archive.short_description = "Archive"

    def view_on_site(self, obj):
        return reverse('source-detail', kwargs={"pk": obj.pk})
