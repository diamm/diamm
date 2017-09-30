from django.contrib import admin
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole
from diamm.models.data.bibliography_publication import BibliographyPublication
from diamm.models.data.source_bibliography import SourceBibliography
from salmonella.admin import SalmonellaMixin
from reversion.admin import VersionAdmin


class SourceInline(admin.TabularInline):
    model = SourceBibliography
    extra = 0


class AuthorsInline(SalmonellaMixin, admin.TabularInline):
    model = BibliographyAuthorRole
    extra = 0
    salmonella_fields = ('bibliography_author',)


class PublicationInline(admin.TabularInline):
    model = BibliographyPublication
    extra = 0


@admin.register(Bibliography)
class BibliographyAdmin(VersionAdmin):
    list_display = ('get_authors', 'title', 'year', 'abbreviation', 'created')
    list_filter = ('type__name',)
    search_fields = ('title', 'authors__bibliography_author__last_name', 'abbreviation')
    inlines = (AuthorsInline, PublicationInline)

    def get_authors(self, obj):
        authors = obj.authors.all()
        if not authors:
            return "[No Author]"

        if len(authors) > 2:
            authlist = ", ".join([a.bibliography_author.full_name for a in authors[:2]])
            return "{0} et al.".format(authlist)
        else:
            authlist = ", ".join([a.bibliography_author.full_name for a in authors])
            return "{0}".format(authlist)
    get_authors.short_description = "Authors"

