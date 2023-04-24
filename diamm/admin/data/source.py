import pysolr
from django.conf import settings
from django.contrib import admin, messages
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.forms import TextInput, Textarea
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from dynamic_raw_id.admin import DynamicRawIDMixin
from pagedown.widgets import AdminPagedownWidget
from rest_framework.reverse import reverse
from reversion.admin import VersionAdmin

from diamm.admin.filters.input_filter import InputFilter
from diamm.admin.forms.copy_inventory import CopyInventoryForm
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.item import Item
from diamm.models.data.page import Page
from diamm.models.data.source import Source
from diamm.models.data.source_bibliography import SourceBibliography
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.source_url import SourceURL
from diamm.signals.item_signals import index_item, delete_item


class SourceCopyistInline(DynamicRawIDMixin, admin.StackedInline):
    model = SourceCopyist
    extra = 0


class SourceRelationshipInline(DynamicRawIDMixin, admin.StackedInline):
    model = SourceRelationship
    extra = 0


class SourceProvenanceInline(DynamicRawIDMixin, admin.StackedInline):
    model = SourceProvenance
    extra = 0
    verbose_name = "Provenance"
    verbose_name_plural = "Provenance"


class BibliographyInline(DynamicRawIDMixin, admin.TabularInline):
    model = SourceBibliography
    verbose_name_plural = "Bibliography Entries"
    verbose_name = "Bibliography Entry"
    extra = 0
    dynamic_raw_id_fields = ('bibliography',)
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
    fields = ('link_id_field', 'numeration', 'sort_order', 'page_type')
    readonly_fields = ('link_id_field',)

    def link_id_field(self, obj):
        change_url = reverse('admin:diamm_data_page_change', args=(obj.pk,))
        return mark_safe('<a href="{0}">{1}</a>'.format(change_url, obj.pk))


class URLsInline(admin.TabularInline):
    model = SourceURL
    extra = 0


class ItemInline(DynamicRawIDMixin, admin.TabularInline):
    model = Item
    extra = 0
    classes = ('collapse',)
    dynamic_raw_id_fields = ('composition',)
    fields = ('link_id_field', 'folio_start', 'folio_end', 'composition', 'get_composers', 'source_order',)
    readonly_fields = ('link_id_field', 'get_composers')

    def get_composers(self, obj):
        if obj.composition:
            return "{0}".format(obj.composition.composer_names)

    def link_id_field(self, obj):
        change_url = reverse('admin:diamm_data_item_change', args=(obj.pk,))
        return mark_safe('<a href="{0}">{1}</a>'.format(change_url, obj.pk))


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


class ArchiveKeyFilter(InputFilter):
    parameter_name = "archive"
    title = "Archive Key"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(archive__id__exact=self.value())


class SourceKeyFilter(InputFilter):
    parameter_name = "source"
    title = "Source Key"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(id__exact=self.value())


@admin.register(Source)
class SourceAdmin(DynamicRawIDMixin, VersionAdmin):
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
               BibliographyInline, SourceRelationshipInline, SourceCopyistInline,
               SourceProvenanceInline, PagesInline, ItemInline)
    list_filter = (
        SourceKeyFilter,
        ArchiveKeyFilter,
        CountryListFilter,
        InventoryFilter
    )
    list_editable = ('sort_order',)
    filter_horizontal = ['notations']
    # actions = (sort_sources,)
    dynamic_raw_id_fields = ('cover_image', 'archive')
    view_on_site = True

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }

    def get_city(self, obj):
        return "{0} ({1})".format(obj.archive.city.name, obj.archive.city.parent.name)
    get_city.short_description = "City"

    def get_archive(self, obj):
        return "{0}".format(obj.archive.name)
    get_archive.short_description = "Archive"

    def copy_inventory_view(self, request, pk):
        instance = Source.objects.get(pk=pk)
        if 'do_action' not in request.POST:
            form = CopyInventoryForm(instance=instance)
        else:
            post_save.disconnect(index_item, sender=Item)
            post_delete.disconnect(delete_item, sender=Item)
            form = CopyInventoryForm(request.POST, instance=instance)
            if not form.is_valid():
                messages.error(request, "There was an error in the form")
            else:
                targets = form.cleaned_data['targets']

                for target in targets:
                    # If the source has accidentally been included in the targets,
                    # skip it.
                    if target.pk == instance.pk:
                        continue

                    print("Copying to {0}".format(target.display_name))
                    self.__copy_items_to_source(instance, target)

                messages.success(request, "Inventories successfully copied.")
                post_save.connect(index_item, sender=Item)
                post_delete.connect(index_item, sender=Item)

                return redirect(
                    'admin:diamm_data_source_change', pk
                )

        return render(request,
                      'admin/diamm_data/source/copy_inventory.html', {
                        'form': form,
                        'instance': instance
                      })

    def get_urls(self):
        urls = super(SourceAdmin, self).get_urls()
        my_urls = [
            path('<int:pk>/copy_inventory/',
                 self.admin_site.admin_view(self.copy_inventory_view),
                 name="copy-inventory")
        ]

        return my_urls + urls

    def __copy_items_to_source(self, source, target):
        # items = source.
        inventory = source.inventory.all()
        # Delete any items on the target source, and clean it up in Solr.
        target.inventory.all().delete()
        self.__delete_items_from_solr(target)

        for item in inventory:
            item.pk = None
            item.source = target
            item.folio_start = None
            item.folio_end = None
            item.save()
            item.pages.clear()

        target.save()

    # TODO: Objects are not being deleted from Solr.
    def __delete_items_from_solr(self, target):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = " AND ".join(["type:item", "source_i:{0}".format(target.pk)])
        results = connection.delete(q=fq)
