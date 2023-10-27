from django.contrib import admin

from diamm.models.data.source_manifest import SourceManifest


@admin.register(SourceManifest)
class SourceManifestAdmin(admin.ModelAdmin):
    pass
