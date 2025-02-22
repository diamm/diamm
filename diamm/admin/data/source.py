import pysolr
from django.conf import settings
from django.contrib import admin, messages
from django.db import models
from django.db.models import Q
from django.forms import Textarea, TextInput
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from pagedown.widgets import AdminPagedownWidget
from rest_framework.reverse import reverse
from reversion.admin import VersionAdmin

from diamm.admin.filters.input_filter import InputFilter
from diamm.admin.forms.copy_inventory import CopyInventoryForm
from diamm.admin.helpers.optimized_raw_id import RawIdWidgetAdminMixin
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.item import Item
from diamm.models.data.page import Page
from diamm.models.data.source import Source
from diamm.models.data.source_authority import SourceAuthority
from diamm.models.data.source_bibliography import SourceBibliography
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.source_url import SourceURL


class SourceCopyistInline(admin.StackedInline):
    model = SourceCopyist
    extra = 0

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive__city__parent", "content_type")
        )


class SourceRelationshipInline(admin.StackedInline):
    model = SourceRelationship
    extra = 0
    # raw_id_fields = ('relationship_type',)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "source__archive__city__parent", "content_type", "relationship_type"
            )
            .prefetch_related("related_entity")
        )


class SourceProvenanceInline(RawIdWidgetAdminMixin, admin.StackedInline):
    model = SourceProvenance
    extra = 0
    verbose_name = "Provenance"
    verbose_name_plural = "Provenance"
    raw_id_fields = ("city", "country", "region", "protectorate")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "source__archive__city__parent",
                "city__parent",
                "country__parent",
                "region__parent",
            )
        )


class BibliographyInline(RawIdWidgetAdminMixin, admin.TabularInline):
    model = SourceBibliography
    verbose_name_plural = "Bibliography Entries"
    verbose_name = "Bibliography Entry"
    extra = 0
    raw_id_fields = ("bibliography",)

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "160"})},
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 40})},
    }

    # def get_bibliography(self, obj):
    #     if not obj.bibliography:
    #         return None
    #     change_url = reverse(
    #         "admin:diamm_data_bibliography_change",
    #         args=(obj.bibliography_id,),
    #     )
    #     return mark_safe(f"<a href='{change_url}'>{obj.bibliography}</a>")  # noqa: S308

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive__city__parent", "bibliography__type")
        )


class IdentifiersInline(admin.TabularInline):
    model = SourceIdentifier
    extra = 0

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive__city__parent")
        )


class AuthoritiesInline(admin.TabularInline):
    model = SourceAuthority
    extra = 0


class NotesInline(admin.TabularInline):
    model = SourceNote
    extra = 0

    formfield_overrides = {models.TextField: {"widget": AdminPagedownWidget}}

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("source__archive__city")


class PagesInline(admin.TabularInline):
    model = Page
    extra = 0
    classes = ("collapse",)
    fields = ("link_id_field", "numeration", "sort_order", "page_type")
    readonly_fields = ("link_id_field",)
    list_select_related = ("source__archive__city",)

    def link_id_field(self, obj):
        change_url = reverse("admin:diamm_data_page_change", args=(obj.pk,))
        return mark_safe(f'<a href="{change_url}">{obj.pk}</a>')  # noqa: S308

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("source__archive__city")


class URLsInline(admin.TabularInline):
    model = SourceURL
    extra = 0


# Uses a custom raw id mixin because of a bug in the built-in mixin
# See: https://deepintodjango.com/reducing-queries-for-foreignkeys-in-django-admin-inlines
class ItemInline(RawIdWidgetAdminMixin, admin.TabularInline):
    model = Item
    extra = 0
    classes = ("collapse",)
    fields = (
        "link_id_field",
        "composition",
        "folio_start",
        "folio_end",
        # "get_composition",
        "get_composers",
        "source_order",
    )
    raw_id_fields = ("composition",)
    readonly_fields = ("link_id_field", "get_composers", "get_composition")

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "10"})},
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive__city__parent__parent", "composition")
            .prefetch_related("composition__composers__composer")
        )

    def get_composition(self, obj):
        if not obj.composition_id:
            return None
        change_url = reverse(
            "admin:diamm_data_composition_change", args=(obj.composition_id,)
        )
        return mark_safe(f'<a href="{change_url}">{obj.composition.title}</a>')  # noqa: S308

    get_composition.short_description = "Composition"

    def get_composers(self, obj):
        if not obj.composition_id:
            return None
        cnames: list = [c.composer.full_name for c in obj.composition.composers.all()]
        return mark_safe("; <br />".join(cnames))  # noqa: S308

    get_composers.short_description = "Composers"

    def link_id_field(self, obj):
        change_url = reverse("admin:diamm_data_item_change", args=(obj.pk,))
        return mark_safe(f'<a href="{change_url}">{obj.pk}</a>')  # noqa: S308


class InventoryFilter(admin.SimpleListFilter):
    title = _("Inventory")
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Source has inventory")),
            ("no", _("Source does not have inventory")),
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
    title = _("Country")
    parameter_name = "country"

    def lookups(self, request, model_admin):
        countries = GeographicArea.objects.filter(
            Q(type=GeographicArea.COUNTRY) | Q(type=GeographicArea.STATE)
        )
        return [(c.id, c.name) for c in countries]

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
class SourceAdmin(VersionAdmin):
    save_on_top = True
    list_display = (
        "shelfmark",
        "name",
        "get_city",
        "get_archive",
        "public",
        "public_images",
        "inventory_provided",
        "sort_order",
        "updated",
    )
    readonly_fields = ("created", "updated")
    search_fields = (
        "identifiers__identifier",
        "name",
        "archive__name",
        "archive__siglum",
        "archive__city__name",
        "shelfmark",
        "=pk",
    )
    inlines = (
        IdentifiersInline,
        NotesInline,
        URLsInline,
        AuthoritiesInline,
        BibliographyInline,
        SourceRelationshipInline,
        SourceCopyistInline,
        SourceProvenanceInline,
        PagesInline,
        ItemInline,
    )
    list_filter = (
        SourceKeyFilter,
        ArchiveKeyFilter,
        CountryListFilter,
        InventoryFilter,
    )
    list_editable = ("sort_order",)
    filter_horizontal = ["notations"]
    # actions = (sort_sources,)
    raw_id_fields = ("cover_image", "archive")
    view_on_site = True
    list_select_related = ("archive__city",)

    formfield_overrides = {models.TextField: {"widget": AdminPagedownWidget}}

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "pages",
                "copyists",
                "notations",
                "links",
                "bibliographies__bibliography",
                "sets",
                "identifiers",
                "authorities",
                "notes",
                "provenance__city",
                "provenance__country",
                "provenance__region",
                "contributions",
                "commentary",
            )
            .select_related(
                "archive__city__parent__parent",
                "cover_image__page",
                "cover_image__type",
            )
        )

    def get_city(self, obj):
        return f"{obj.archive.city.name} ({obj.archive.city.parent.name})"

    get_city.short_description = "City"

    def get_archive(self, obj):
        return f"{obj.archive.name}"

    get_archive.short_description = "Archive"

    def copy_inventory_view(self, request, pk):
        instance = Source.objects.get(pk=pk)
        if "do_action" not in request.POST:
            form = CopyInventoryForm(instance=instance)
        else:
            form = CopyInventoryForm(request.POST, instance=instance)
            if not form.is_valid():
                messages.error(request, "There was an error in the form")
            else:
                targets = form.cleaned_data["targets"]

                for target in targets:
                    # If the source has accidentally been included in the targets,
                    # skip it.
                    if target.pk == instance.pk:
                        continue

                    self.__copy_items_to_source(instance, target)

                messages.success(request, "Inventories successfully copied.")

                return redirect("admin:diamm_data_source_change", pk)

        return render(
            request,
            "admin/diamm_data/source/copy_inventory.html",
            {"form": form, "instance": instance},
        )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "<int:pk>/copy_inventory/",
                self.admin_site.admin_view(self.copy_inventory_view),
                name="copy-inventory",
            )
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
        connection = pysolr.Solr(settings.SOLR["SERVER"])
        fq = " AND ".join(["type:item", f"source_i:{target.pk}"])
        _ = connection.delete(q=fq)
