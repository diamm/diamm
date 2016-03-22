from django.contrib import admin
from diamm.models.data.bibliography_author import BibliographyAuthor
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole


class BibliographyInline(admin.TabularInline):
    model = BibliographyAuthorRole
    extra = 0
    raw_id_fields = ('bibliography_entry',)


@admin.register(BibliographyAuthor)
class BibliographyAuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name',)
    inlines = (BibliographyInline,)
