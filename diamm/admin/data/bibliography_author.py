from django.contrib import admin
from diamm.models.data.bibliography_author import BibliographyAuthor


@admin.register(BibliographyAuthor)
class BibliographyAuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name',)
