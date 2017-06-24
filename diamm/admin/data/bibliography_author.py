from django.contrib import admin
from diamm.models.data.bibliography_author import BibliographyAuthor
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole
from salmonella.admin import SalmonellaMixin


class BibliographyInline(SalmonellaMixin, admin.TabularInline):
    model = BibliographyAuthorRole
    extra = 0
    salmonella_fields = ('bibliography_entry',)


@admin.register(BibliographyAuthor)
class BibliographyAuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name',)
    inlines = (BibliographyInline,)
