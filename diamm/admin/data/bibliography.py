from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole
from diamm.models.data.bibliography_publication import BibliographyPublication
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
    inlines = (AuthorsInline, PublicationInline)

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
