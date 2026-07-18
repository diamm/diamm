from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import reverse
from reversion.admin import VersionAdmin

from diamm.admin.forms.merge_bibliographies import MergeBibliographiesForm
from diamm.admin.helpers.html import admin_change_link
from diamm.admin.merge_models import MergeConflictError
from diamm.models import CompositionBibliography
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole
from diamm.models.data.bibliography_publication import BibliographyPublication
from diamm.models.data.item_bibliography import ItemBibliography
from diamm.models.data.set_bibliography import SetBibliography
from diamm.models.data.source_bibliography import SourceBibliography
from diamm.services.bibliography import merge_bibliographies


class SourceInline(admin.TabularInline):
    model = SourceBibliography
    extra = 0


class AuthorsInline(admin.TabularInline):
    model = BibliographyAuthorRole
    extra = 0
    autocomplete_fields = ("bibliography_author",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("bibliography_author", "bibliography_entry")
        )


class PublicationInline(admin.TabularInline):
    model = BibliographyPublication
    extra = 0


class SourceBibliographyInline(admin.TabularInline):
    model = SourceBibliography
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def attached_to_source(self, obj):
        change_url = reverse("admin:diamm_data_source_change", args=(obj.source.id,))
        return admin_change_link(
            change_url, f"{obj.source.archive.siglum} {obj.source.shelfmark}"
        )

    fields = ("attached_to_source",)
    readonly_fields = ("attached_to_source",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("source", "source__archive", "bibliography").all()


class ItemBibliographyInline(admin.TabularInline):
    model = ItemBibliography
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def attached_to_item(self, obj):
        change_url = reverse("admin:diamm_data_item_change", args=(obj.item.id,))
        return admin_change_link(change_url, obj.item)

    fields = ("attached_to_item",)
    readonly_fields = ("attached_to_item",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("item", "item__source__archive", "bibliography").all()


class CompositionBibliographyInline(admin.TabularInline):
    model = CompositionBibliography
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def attached_to_composition(self, obj):
        change_url = reverse(
            "admin:diamm_data_composition_change", args=(obj.composition.id,)
        )
        return admin_change_link(change_url, obj.composition.title)

    fields = ("attached_to_composition",)
    readonly_fields = ("attached_to_composition",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("composition", "bibliography").all()


class SetBibliographyInline(admin.TabularInline):
    model = SetBibliography
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    @admin.display(description="Set")
    def attached_to_set(self, obj):
        change_url = reverse("admin:diamm_data_set_change", args=(obj.set_id,))
        return admin_change_link(change_url, str(obj.set))

    fields = ("attached_to_set",)
    readonly_fields = ("attached_to_set",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("set", "bibliography")


@admin.register(Bibliography)
class BibliographyAdmin(VersionAdmin):
    list_display = ("get_authors", "title", "year", "abbreviation", "created", "id")
    list_filter = ("type__name",)
    search_fields = (
        "=id",
        "title",
        "authors__bibliography_author__last_name",
        "abbreviation",
    )
    readonly_fields = ("id",)
    inlines = (
        AuthorsInline,
        PublicationInline,
        SourceBibliographyInline,
        ItemBibliographyInline,
        CompositionBibliographyInline,
        SetBibliographyInline,
    )
    actions = ("merge_bibliographies_action",)

    @admin.action(description="Merge bibliography entries")
    def merge_bibliographies_action(self, request, queryset):
        if "do_action" in request.POST:
            form = MergeBibliographiesForm(request.POST, queryset=queryset)
            if form.is_valid():
                target = form.cleaned_data["target"]
                aliases = list(queryset.exclude(pk=target.pk))
                try:
                    merge_bibliographies(
                        target,
                        aliases,
                        keep_old=form.cleaned_data["keep_old"],
                    )
                except MergeConflictError as exc:
                    messages.error(request, str(exc))
                else:
                    messages.success(
                        request,
                        "Bibliography entries successfully merged. Reindex to publish the updated citations.",
                    )
                    return None
            else:
                messages.error(request, "There was an error merging these entries.")
        else:
            form = MergeBibliographiesForm(queryset=queryset)

        return render(
            request,
            "admin/bibliography/merge_bibliographies.html",
            {
                **self.admin_site.each_context(request),
                "objects": queryset,
                "form": form,
                "opts": self.model._meta,
                "title": "Merge bibliography entries",
            },
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related("type")
            .prefetch_related("authors__bibliography_author")
            .all()
        )

    @admin.display(
        description="Authors", ordering="authors__bibliography_author__last_name"
    )
    def get_authors(self, obj):
        authors = obj.authors.all()
        if not authors:
            return "[No Author]"

        if len(authors) > 2:
            authlist = ", ".join([a.bibliography_author.full_name for a in authors[:2]])
            return f"{authlist} et al."
        else:
            authlist = ", ".join([a.bibliography_author.full_name for a in authors])
            return f"{authlist}"
