from django.contrib import admin
from diamm.models.data.source_catalogue_entry import SourceCatalogueEntry


@admin.register(SourceCatalogueEntry)
class SourceCatalogueEntryAdmin(admin.ModelAdmin):
    pass
