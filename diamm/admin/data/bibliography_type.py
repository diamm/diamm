from django.contrib import admin

from diamm.models.data.bibliography_type import BibliographyType


@admin.register(BibliographyType)
class BibliographyTypeAdmin(admin.ModelAdmin):
    pass
