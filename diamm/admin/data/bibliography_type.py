from diamm.models.data.bibliography_type import BibliographyType
from django.contrib import admin


@admin.register(BibliographyType)
class BibliographyTypeAdmin(admin.ModelAdmin):
    pass
