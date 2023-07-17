from diamm.models.data.source_catalogue_entry import SourceCatalogueEntry
from django.contrib import admin


@admin.register(SourceCatalogueEntry)
class SourceCatalogueEntryAdmin(admin.ModelAdmin):
    pass
