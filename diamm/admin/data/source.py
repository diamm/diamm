from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.db.models import Q
from django.forms import Textarea, TextInput
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin

from diamm.admin.filters.input_filter import InputFilter
from diamm.admin.forms.copy_inventory import CopyInventoryForm
from diamm.admin.forms.create_pages_and_images import CreatePagesAndImagesForm
from diamm.admin.helpers.html import admin_change_link, html_join
from diamm.admin.helpers.optimized_raw_id import RawIdWidgetAdminMixin
from diamm.models import Image, ItemBibliography, ItemComposer, ItemNote, Voice
from diamm.models.data.geographic_area import AreaTypeChoices, GeographicArea
from diamm.models.data.item import Item
from diamm.models.data.item_note import ItemNoteTypeChoices
from diamm.models.data.page import Page, PageTypeChoices
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
    classes = ("collapse",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive__city__parent", "content_type")
        )


class SourceRelationshipInline(admin.StackedInline):
    model = SourceRelationship
    extra = 0
    classes = ("collapse",)

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
    classes = ("collapse",)

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
    classes = ("collapse",)

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
    classes = ("collapse",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive__city__parent")
        )


class AuthoritiesInline(admin.TabularInline):
    model = SourceAuthority
    extra = 0
    classes = ("collapse",)


class NotesInline(admin.TabularInline):
    model = SourceNote
    classes = ("collapse",)
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
        return admin_change_link(change_url, obj.pk)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("source__archive__city")


class URLsInline(admin.TabularInline):
    model = SourceURL
    extra = 0
    classes = ("collapse",)


# Uses a custom raw id mixin because of a bug in the built-in mixin
# See: https://deepintodjango.com/reducing-queries-for-foreignkeys-in-django-admin-inlines
class ItemInline(RawIdWidgetAdminMixin, admin.TabularInline):
    model = Item
    extra = 0
    classes = ("collapse",)
    fields = (
        "link_id_field",
        "composition",
        "fragment",
        "completeness",
        "item_title",
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

    @admin.display(description="Composition")
    def get_composition(self, obj):
        if not obj.composition_id:
            return None
        change_url = reverse(
            "admin:diamm_data_composition_change", args=(obj.composition_id,)
        )
        return admin_change_link(change_url, obj.composition.title)

    @admin.display(description="Composers")
    def get_composers(self, obj) -> str:
        if obj.composition_id:
            cnames: list = [
                c.composer.full_name for c in obj.composition.composers.all()
            ]
            return html_join(cnames)
        elif obj.unattributed_composers:
            unatt_names: list = [
                f"[{c.composer.full_name}]" for c in obj.unattributed_composers.all()
            ]
            return html_join(unatt_names)
        return "-"

    def link_id_field(self, obj):
        change_url = reverse("admin:diamm_data_item_change", args=(obj.pk,))
        return admin_change_link(change_url, obj.pk)


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
            Q(type=AreaTypeChoices.COUNTRY) | Q(type=AreaTypeChoices.STATE)
        )
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
        "public",
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
        return super().get_queryset(request).select_related(
            "archive__city__parent"
        )

    @admin.display(description="City")
    def get_city(self, obj):
        city = obj.archive.city
        if city is None:
            return "-"
        if city.parent is None:
            return city.name
        return f"{city.name} ({city.parent.name})"

    @admin.display(description="Archive")
    def get_archive(self, obj):
        return f"{obj.archive.name}"

    def copy_inventory_view(self, request, pk):
        source = self.get_object(request, str(pk))
        if source is None:
            raise Http404
        if not self.has_change_permission(request, source):
            raise PermissionDenied

        if "do_action" not in request.POST:
            form = CopyInventoryForm(instance=source)
        else:
            form = CopyInventoryForm(request.POST, instance=source)
            if not form.is_valid():
                messages.error(request, "There was an error in the form")
            else:
                targets = form.cleaned_data["targets"]

                with transaction.atomic():
                    for target in targets:
                        # If the source has accidentally been included in the targets,
                        # skip it.
                        if target.pk == source.pk:
                            continue

                        self.__copy_items_to_source(source, target)

                messages.success(
                    request, "Inventories successfully copied. Now go check them!"
                )

                return redirect("admin:diamm_data_source_change", pk)

        return render(
            request,
            "admin/diamm_data/source/copy_inventory.html",
            {
                **self.admin_site.each_context(request),
                "form": form,
                "instance": source,
                "opts": self.model._meta,
                "title": "Copy inventory",
            },
        )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "<int:pk>/copy_inventory/",
                self.admin_site.admin_view(self.copy_inventory_view),
                name="copy-inventory",
            ),
            path(
                "<int:pk>/import_images/",
                self.admin_site.admin_view(self.import_images),
                name="import-images",
            ),
        ]

        return my_urls + urls

    @transaction.atomic
    def __copy_items_to_source(self, source, target):
        items = list(
            source.inventory.all().prefetch_related(
                "voices",
                "notes",
                "itembibliography_set",
                "unattributed_composers",
            )
        )

        target.inventory.all().delete()

        new_items = [
            Item(
                source=target,
                **self._copy_concrete_fields(item, exclude={"id", "source"}),
            )
            for item in items
        ]
        Item.objects.bulk_create(new_items)
        if any(item.pk is None for item in new_items):
            raise RuntimeError("The database did not return IDs for copied items")

        new_voices = []
        new_bibs = []
        new_comps = []
        new_item_notes = []

        for old_item, new_item in zip(items, new_items, strict=True):
            for v in old_item.voices.all():
                new_voices.append(
                    Voice(
                        item=new_item,
                        **self._copy_concrete_fields(v, exclude={"id", "item"}),
                    )
                )

            for n in old_item.notes.all():
                new_item_notes.append(
                    ItemNote(
                        item=new_item,
                        **self._copy_concrete_fields(n, exclude={"id", "item"}),
                    )
                )

            for b in old_item.itembibliography_set.all():
                new_bibs.append(
                    ItemBibliography(
                        item=new_item,
                        **self._copy_concrete_fields(b, exclude={"id", "item"}),
                    )
                )

            for c in old_item.unattributed_composers.all():
                new_comps.append(
                    ItemComposer(
                        item=new_item,
                        **self._copy_concrete_fields(c, exclude={"id", "item"}),
                    )
                )

            new_item_notes.append(
                ItemNote(
                    item=new_item,
                    type=ItemNoteTypeChoices.INTERNAL,
                    note=f"Bulk copied from source {source.pk}",
                )
            )

        Voice.objects.bulk_create(new_voices)
        ItemBibliography.objects.bulk_create(new_bibs)
        ItemComposer.objects.bulk_create(new_comps)
        ItemNote.objects.bulk_create(new_item_notes)

    @staticmethod
    def _copy_concrete_fields(instance, *, exclude):
        return {
            field.attname: getattr(instance, field.attname)
            for field in instance._meta.concrete_fields
            if field.name not in exclude and field.attname not in exclude
        }

    @transaction.atomic
    def import_images(self, request, pk):
        source = self.get_object(request, str(pk))
        if source is None:
            raise Http404
        if not self.has_change_permission(request, source):
            raise PermissionDenied

        if "do_action" not in request.POST:
            form = CreatePagesAndImagesForm()
        else:
            form = CreatePagesAndImagesForm(request.POST)
            if not form.is_valid():
                messages.error(request, "There was an error in the form.")
            else:
                import_lines_t = form.cleaned_data["imports"]
                make_public_b = form.cleaned_data["public"]
                import_lines = import_lines_t.splitlines()

                # Check that all lines are well-formatted before importing any
                processed_lines = []
                for i, line in enumerate(import_lines):
                    try:
                        plabel, iloc = line.split("|")
                        processed_lines.append((plabel, iloc))

                    except ValueError:
                        messages.error(
                            request,
                            f"Line {i} is not formatted correctly. It is: {line}. Cancelled import.",
                        )
                        return redirect("admin:diamm_data_source_change", pk)

                source.pages.all().delete()

                for i, line in enumerate(processed_lines):
                    p = Page(
                        source=source,
                        numeration=line[0],
                        sort_order=i,
                        page_type=PageTypeChoices.PAGE,
                    )
                    p.save()

                    i = Image(page=p, location=line[1], public=make_public_b)
                    i.save()

                messages.success(
                    request, "Pages and images successfully created. Now go check them!"
                )

                return redirect("admin:diamm_data_source_change", pk)

        return render(
            request,
            "admin/diamm_data/source/import_images.html",
            context={
                **self.admin_site.each_context(request),
                "form": form,
                "instance": source,
                "opts": self.model._meta,
                "title": "Import images",
            },
        )
