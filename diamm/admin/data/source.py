from django.contrib import admin, messages
from django.db import models, transaction
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
from diamm.admin.forms.create_pages_and_images import CreatePagesAndImagesForm
from diamm.admin.helpers.optimized_raw_id import RawIdWidgetAdminMixin
from diamm.models import ItemBibliography, ItemComposer, ItemNote, Voice, Image
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
        return mark_safe(f'<a href="{change_url}">{obj.pk}</a>')  # noqa: S308

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
        return mark_safe(f'<a href="{change_url}">{obj.composition.title}</a>')  # noqa: S308

    @admin.display(description="Composers")
    def get_composers(self, obj) -> str:
        if obj.composition_id:
            cnames: list = [
                c.composer.full_name for c in obj.composition.composers.all()
            ]
            return mark_safe("; <br />".join(cnames))  # noqa: S308
        elif obj.unattributed_composers:
            unatt_names: list = [
                f"[{c.composer.full_name}]" for c in obj.unattributed_composers.all()
            ]
            return mark_safe("; <br />".join(unatt_names))  # noqa: S308
        return "-"

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

    @admin.display(description="City")
    def get_city(self, obj):
        return f"{obj.archive.city.name} ({obj.archive.city.parent.name})"

    @admin.display(description="Archive")
    def get_archive(self, obj):
        return f"{obj.archive.name}"

    def copy_inventory_view(self, request, pk):
        source = Source.objects.get(pk=pk)
        if "do_action" not in request.POST:
            form = CopyInventoryForm(instance=source)
        else:
            form = CopyInventoryForm(request.POST, instance=source)
            if not form.is_valid():
                messages.error(request, "There was an error in the form")
            else:
                targets = form.cleaned_data["targets"]

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
            {"form": form, "instance": source},
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
        # Prefetch related data efficiently
        items = list(
            source.inventory.all().prefetch_related(
                "voices",
                "notes",
                "itembibliography_set",
                "unattributed_composers",
            )
        )

        # Clear existing target inventory
        target.inventory.all().delete()

        # Clone all Items (in memory)
        new_items = []
        old_to_new_item_map = {}

        for item in items:
            old_id = item.pk
            item.pk = None
            item.source = target
            new_items.append(item)
            # Temporarily store mapping (will update after bulk_create)
            old_to_new_item_map[old_id] = item

        # Bulk-create all new Items
        Item.objects.bulk_create(new_items)

        # Refresh PKs for the new items
        # Django doesn't auto-populate PKs unless using PostgreSQL + `return_defaults=True`
        # So we re-fetch in the same order:
        new_items = list(target.inventory.all().order_by("pk"))
        for old_item, new_item in zip(items, new_items, strict=True):
            old_to_new_item_map[old_item.pk] = new_item

        # Build up related clones (using the old→new mapping)
        new_voices = []
        new_bibs = []
        new_comps = []
        new_item_notes = []

        for old_item in items:
            new_item = old_to_new_item_map[old_item.pk]

            for v in old_item.voices.all():
                v.pk = None
                v.item = new_item
                new_voices.append(v)

            for n in old_item.notes.all():
                n.pk = None
                n.item = new_item
                new_item_notes.append(n)

            for b in old_item.itembibliography_set.all():
                b.pk = None
                b.item = new_item
                new_bibs.append(b)

            for c in old_item.unattributed_composers.all():
                c.pk = None
                c.item = new_item
                new_comps.append(c)

            new_item_notes.append(
                ItemNote(
                    item=new_item,
                    type=ItemNoteTypeChoices.INTERNAL,
                    note=f"Bulk copied from source {source.pk}",
                )
            )

        # 5️⃣ Bulk-create all related data
        Voice.objects.bulk_create(new_voices)
        ItemBibliography.objects.bulk_create(new_bibs)
        ItemComposer.objects.bulk_create(new_comps)
        ItemNote.objects.bulk_create(new_item_notes)

    def import_images(self, request, pk):
        source = Source.objects.get(pk=pk)
        if "do_action" not in request.POST:
            form = CreatePagesAndImagesForm()
        else:
            form = CreatePagesAndImagesForm(request.POST)
            if not form.is_valid():
                messages.error(request, "There was an error in the form.")
            else:
                source.pages.all().delete()

                import_lines_t = form.cleaned_data["imports"]
                make_public_b = form.cleaned_data["public"]
                import_lines = import_lines_t.split("\n")

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

                # If all lines pass, now import them.
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
            context={"form": form, "instance": source},
        )
