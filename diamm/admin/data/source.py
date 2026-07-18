from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import models, transaction
from django.db.models import Q
from django.forms import Textarea, TextInput, TypedChoiceField
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin

from diamm.admin.filters.input_filter import InputFilter
from diamm.admin.forms.copy_inventory import CopyInventoryForm
from diamm.admin.forms.create_pages_and_images import CreatePagesAndImagesForm
from diamm.admin.forms.virtual_source import DonorSourceForm, VirtualSourcePagesForm
from diamm.admin.helpers.html import html_join
from diamm.admin.helpers.optimized_raw_id import RawIdWidgetAdminMixin
from diamm.admin.helpers.source_picker import source_picker_label
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
from diamm.models.data.source_to_source_relationship import SourceToSourceRelationship
from diamm.models.data.source_url import SourceURL
from diamm.services.virtual_sources import copy_pages_to_virtual_source


class EntityContentTypeChoiceMixin:
    """Build small repeated inline choice lists once per admin request."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name not in {"content_type", "relationship_type"}:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        cache_name = f"_diamm_{db_field.name}_choices"
        cached = getattr(request, cache_name, None)
        if cached is None:
            queryset = db_field.remote_field.model.objects.all()
            if db_field.name == "content_type":
                queryset = queryset.filter(db_field.get_limit_choices_to()).order_by(
                    "app_label", "model"
                )
            related_objects = list(queryset)
            choices = [
                (str(related_object.pk), str(related_object))
                for related_object in related_objects
            ]
            objects = {
                str(related_object.pk): related_object
                for related_object in related_objects
            }
            cached = (choices, objects)
            setattr(request, cache_name, cached)

        choices, objects = cached
        return TypedChoiceField(
            choices=[("", "---------"), *choices],
            coerce=lambda value: objects[str(value)],
            empty_value=None,
            required=not db_field.blank,
            label=capfirst(db_field.verbose_name),
            help_text=db_field.help_text,
        )


class SourceCopyistInline(EntityContentTypeChoiceMixin, admin.StackedInline):
    model = SourceCopyist
    extra = 0
    classes = ("collapse",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive__city__parent", "content_type")
            .prefetch_related("copyist")
        )


class SourceRelationshipInline(EntityContentTypeChoiceMixin, admin.StackedInline):
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


class OutgoingSourceRelationshipInline(admin.TabularInline):
    model = SourceToSourceRelationship
    fk_name = "from_source"
    extra = 0
    autocomplete_fields = ("to_source",)
    classes = ("collapse",)


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
            .prefetch_related("bibliography__authors__bibliography_author")
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


class URLsInline(admin.TabularInline):
    model = SourceURL
    extra = 0
    classes = ("collapse",)


class SourceInventoryEditorInline(RawIdWidgetAdminMixin, admin.TabularInline):
    """Formset configuration for the dedicated Source inventory editor."""

    model = Item
    extra = 1
    fields = (
        "composition",
        "fragment",
        "completeness",
        "item_title",
        "folio_start",
        "folio_end",
        "source_order",
    )
    raw_id_fields = ("composition",)
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "10"})},
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("composition")
            .prefetch_related("composition__composers__composer")
        )

    @staticmethod
    def composer_display(item):
        if not item.pk or not item.composition_id:
            return "-"
        return (
            html_join(
                composer.composer.full_name
                for composer in item.composition.composers.all()
            )
            or "-"
        )


class SourcePagesEditorInline(admin.TabularInline):
    """Formset configuration for the dedicated Source pages editor."""

    model = Page
    extra = 1
    fields = ("numeration", "sort_order", "page_type", "external")


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
        "is_virtual",
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
        OutgoingSourceRelationshipInline,
        SourceCopyistInline,
        SourceProvenanceInline,
    )
    list_filter = (
        "public",
        "is_virtual",
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
        return super().get_queryset(request).select_related("archive__city__parent")

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

    def add_virtual_pages_view(self, request, pk):
        target = self.get_object(request, str(pk))
        if target is None or not target.is_virtual:
            raise Http404
        required_permissions = (
            self.has_change_permission(request, target),
            request.user.has_perm("diamm_data.add_page"),
            request.user.has_perm("diamm_data.add_image"),
            request.user.has_perm("diamm_data.add_item"),
        )
        if not all(required_permissions):
            raise PermissionDenied

        donor_id = request.POST.get("donor") or request.GET.get("donor")
        donor = Source.objects.filter(pk=donor_id, is_virtual=False).first()
        donor_form = DonorSourceForm(
            request.POST or None, target=target, admin_site=self.admin_site
        )
        page_form = None
        preview = None

        if donor is not None:
            page_form = VirtualSourcePagesForm(
                request.POST or None, target=target, donor=donor
            )
            if request.method == "POST" and (
                "preview" in request.POST or "do_action" in request.POST
            ):
                if page_form.is_valid():
                    preview = page_form.preview_counts
                    if "do_action" in request.POST:
                        result = copy_pages_to_virtual_source(
                            target=target,
                            donor=donor,
                            pages=page_form.cleaned_data["pages"],
                            relationship_type=page_form.cleaned_data[
                                "relationship_type"
                            ],
                        )
                        page_admin = self.admin_site.get_model_admin(Page)
                        image_admin = self.admin_site.get_model_admin(Image)
                        item_admin = self.admin_site.get_model_admin(Item)
                        for page in result.pages:
                            page_admin.log_addition(
                                request, page, "Copied into a virtual source."
                            )
                        for image in result.images:
                            image_admin.log_addition(
                                request, image, "Copied into a virtual source."
                            )
                        for item in result.items:
                            item_admin.log_addition(
                                request, item, "Copied into a virtual source."
                            )
                        if result.relationship_created:
                            relationship = SourceToSourceRelationship.objects.get(
                                from_source=target,
                                to_source=donor,
                                relationship_type=page_form.cleaned_data[
                                    "relationship_type"
                                ],
                            )
                            self.admin_site.get_model_admin(
                                SourceToSourceRelationship
                            ).log_addition(
                                request,
                                relationship,
                                "Created while copying pages into a virtual source.",
                            )
                        messages.success(
                            request,
                            f"Copied {len(result.pages)} page(s), {len(result.images)} image(s), "
                            f"and created {len(result.items)} item(s). Reindex the source to publish the changes.",
                        )
                        return redirect("admin:diamm_data_source_change", target.pk)
            elif request.method == "POST":
                messages.error(request, "There was an error in the form.")
        elif request.method == "POST" and donor_form.is_valid():
            return redirect(
                f"{reverse('admin:add-virtual-pages', args=(target.pk,))}?donor={donor_form.cleaned_data['donor'].pk}"
            )

        return render(
            request,
            "admin/diamm_data/source/add_virtual_pages.html",
            {
                **self.admin_site.each_context(request),
                "instance": target,
                "opts": self.model._meta,
                "title": f"Add pages to {target.display_name}",
                "donor": donor,
                "donor_form": donor_form,
                "page_form": page_form,
                "preview": preview,
            },
        )

    def inventory_view(self, request, pk):
        source = self.get_object(request, str(pk))
        if source is None:
            raise Http404
        if not self.has_change_permission(request, source) or not request.user.has_perm(
            "diamm_data.change_item"
        ):
            raise PermissionDenied

        inventory_inline = SourceInventoryEditorInline(self.model, self.admin_site)
        queryset = inventory_inline.get_queryset(request).filter(source=source)
        paginator = Paginator(queryset, 50)
        page_obj = paginator.get_page(request.GET.get("page"))
        page_ids = [item.pk for item in page_obj.object_list]
        page_queryset = queryset.filter(pk__in=page_ids)

        formset_class = inventory_inline.get_formset(
            request,
            source,
            extra=int(request.user.has_perm("diamm_data.add_item")),
        )
        formset = formset_class(
            request.POST or None,
            instance=source,
            queryset=page_queryset,
            prefix="inventory",
        )
        for form in formset.forms:
            form.composer_display = inventory_inline.composer_display(form.instance)

        if request.method == "POST" and formset.is_valid():
            item_admin = self.admin_site.get_model_admin(Item)
            deleted_ids = [
                form.instance.pk
                for form in formset.deleted_forms
                if form.instance.pk is not None
            ]
            with transaction.atomic():
                if deleted_ids:
                    item_admin.log_deletions(
                        request, Item.objects.filter(pk__in=deleted_ids)
                    )
                formset.save()
                for item in formset.new_objects:
                    item_admin.log_addition(
                        request, item, "Added through the Source inventory editor."
                    )
                for item, changed_fields in formset.changed_objects:
                    item_admin.log_change(
                        request,
                        item,
                        [{"changed": {"fields": changed_fields}}],
                    )
            messages.success(request, "The source inventory was updated successfully.")
            url = reverse("admin:source-inventory", args=(source.pk,))
            if page_obj.number > 1:
                url += f"?page={page_obj.number}"
            return redirect(url)

        return render(
            request,
            "admin/diamm_data/source/inventory.html",
            {
                **self.admin_site.each_context(request),
                "formset": formset,
                "instance": source,
                "opts": self.model._meta,
                "page_obj": page_obj,
                "title": f"Edit inventory: {source.display_name}",
            },
        )

    def pages_view(self, request, pk):
        source = self.get_object(request, str(pk))
        if source is None:
            raise Http404
        if not self.has_change_permission(request, source) or not request.user.has_perm(
            "diamm_data.change_page"
        ):
            raise PermissionDenied

        pages_inline = SourcePagesEditorInline(self.model, self.admin_site)
        queryset = pages_inline.get_queryset(request).filter(source=source)
        paginator = Paginator(queryset, 50)
        page_obj = paginator.get_page(request.GET.get("page"))
        page_ids = [page.pk for page in page_obj.object_list]
        page_queryset = queryset.filter(pk__in=page_ids)

        formset_class = pages_inline.get_formset(
            request,
            source,
            extra=int(request.user.has_perm("diamm_data.add_page")),
        )
        formset = formset_class(
            request.POST or None,
            instance=source,
            queryset=page_queryset,
            prefix="pages",
        )

        if request.method == "POST" and formset.is_valid():
            page_admin = self.admin_site.get_model_admin(Page)
            deleted_ids = [
                form.instance.pk
                for form in formset.deleted_forms
                if form.instance.pk is not None
            ]
            with transaction.atomic():
                if deleted_ids:
                    orphaned_copies = Item.objects.filter(
                        copied_from__isnull=False,
                        pages__pk__in=deleted_ids,
                    ).exclude(pages__pk__in=Page.objects.exclude(pk__in=deleted_ids))
                    self.admin_site.get_model_admin(Item).log_deletions(
                        request, orphaned_copies.distinct()
                    )
                    page_admin.log_deletions(
                        request, Page.objects.filter(pk__in=deleted_ids)
                    )
                formset.save()
                for page in formset.new_objects:
                    page_admin.log_addition(
                        request, page, "Added through the Source pages editor."
                    )
                for page, changed_fields in formset.changed_objects:
                    page_admin.log_change(
                        request,
                        page,
                        [{"changed": {"fields": changed_fields}}],
                    )
            messages.success(request, "The source pages were updated successfully.")
            url = reverse("admin:source-pages", args=(source.pk,))
            if page_obj.number > 1:
                url += f"?page={page_obj.number}"
            return redirect(url)

        return render(
            request,
            "admin/diamm_data/source/pages.html",
            {
                **self.admin_site.each_context(request),
                "formset": formset,
                "instance": source,
                "opts": self.model._meta,
                "page_obj": page_obj,
                "title": f"Edit pages: {source.display_name}",
            },
        )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "virtual-source-donor-autocomplete/",
                self.admin_site.admin_view(self.virtual_source_donor_autocomplete_view),
                name="virtual-source-donor-autocomplete",
            ),
            path(
                "<int:pk>/add_virtual_pages/",
                self.admin_site.admin_view(self.add_virtual_pages_view),
                name="add-virtual-pages",
            ),
            path(
                "<int:pk>/copy_inventory/",
                self.admin_site.admin_view(self.copy_inventory_view),
                name="copy-inventory",
            ),
            path(
                "<int:pk>/inventory/",
                self.admin_site.admin_view(self.inventory_view),
                name="source-inventory",
            ),
            path(
                "<int:pk>/pages/",
                self.admin_site.admin_view(self.pages_view),
                name="source-pages",
            ),
            path(
                "<int:pk>/import_images/",
                self.admin_site.admin_view(self.import_images),
                name="import-images",
            ),
        ]

        return my_urls + urls

    def virtual_source_donor_autocomplete_view(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

        term = request.GET.get("q", "").strip()
        sources = (
            Source.objects.filter(is_virtual=False, pages__isnull=False)
            .select_related("archive")
            .distinct()
        )
        if term:
            search = (
                Q(archive__siglum__icontains=term)
                | Q(shelfmark__icontains=term)
                | Q(name__icontains=term)
                | Q(date_statement__icontains=term)
            )
            if term.isdigit():
                search |= Q(pk=int(term))
            sources = sources.filter(search)

        paginator = Paginator(
            sources.order_by("archive__siglum", "shelfmark", "pk"), 20
        )
        page = paginator.get_page(request.GET.get("page", 1))
        return JsonResponse(
            {
                "results": [
                    {"id": str(source.pk), "text": source_picker_label(source)}
                    for source in page.object_list
                ],
                "pagination": {"more": page.has_next()},
            }
        )

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
