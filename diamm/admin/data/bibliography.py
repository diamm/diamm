from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from diamm.models import CompositionBibliography
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole
from diamm.models.data.bibliography_publication import BibliographyPublication
from diamm.models.data.item_bibliography import ItemBibliography
from diamm.models.data.source_bibliography import SourceBibliography


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
        return mark_safe(  # noqa: S308
            f'<a href="{change_url}">{obj.source.archive.siglum} {obj.source.shelfmark}</a>'
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
        return mark_safe(  # noqa: S308
            f'<a href="{change_url}">{obj.item}</a>'
        )

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
        return mark_safe(  # noqa: S308
            f'<a href="{change_url}">{obj.composition.title}</a>'
        )

    fields = ("attached_to_composition",)
    readonly_fields = ("attached_to_composition",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("composition", "bibliography").all()


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
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related("type")
            .prefetch_related("authors__bibliography_author")
            .all()
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

    get_authors.short_description = "Authors"
    get_authors.admin_order_field = "authors__bibliography_author__last_name"
