import pysolr
from django.contrib import admin, messages
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.forms import TextInput, Textarea
from django.conf.urls import url
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin
from pagedown.widgets import AdminPagedownWidget
from salmonella.admin import SalmonellaMixin
from rest_framework.reverse import reverse
from diamm.admin.forms.copy_inventory import CopyInventoryForm
from diamm.models.data.item import Item
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.source import Source
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_url import SourceURL
from diamm.models.data.source_bibliography import SourceBibliography
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.page import Page
from diamm.signals.item_signals import index_item, delete_item


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
    fields = ('link_id_field', 'folio_start', 'folio_end', 'composition', 'get_composers', 'source_order',)
    readonly_fields = ('link_id_field', 'folio_start', 'folio_end', 'composition', 'get_composers')

    def get_composers(self, obj):
        if obj.composition:
            return "{0}".format(obj.composition.composer_names)

    def link_id_field(self, obj):
        change_url = reverse('admin:diamm_data_item_change', args=(obj.pk,))
        return '<a href="{0}">{1}</a>'.format(change_url, obj.pk)
    link_id_field.allow_tags = True


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
            url(r'^(?P<pk>[0-9]+)/copy_inventory/$',
                self.admin_site.admin_view(self.copy_inventory_view),
                name="copy-inventory")
        ]

        return my_urls + urls

    def __copy_items_to_source(self, source, target):
        # items = source.
        inventory = source.inventory.all()
        # Delete any items on the target source, and clean it up in Solr.
        print("Deleting any existing objects")
        target.inventory.all().delete()
        self.__delete_items_from_solr(target)

        print("Indexing items")
        for item in inventory:
            item.pk = None
            item.source = target
            item.folio_start = None
            item.folio_end = None
            item.save()
            item.pages.clear()
            print("Item {0} saved".format(item.pk))

        target.save()

    # TODO: Objects are not being deleted from Solr.
    def __delete_items_from_solr(self, target):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ["type:item", "source_i:{0}".format(target.pk)]
        results = connection.delete(q=fq)
