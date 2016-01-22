from django.contrib import admin
from diamm.models.data.source_copyist import SourceCopyist


@admin.register(SourceCopyist)
class SourceCopyistAdmin(admin.ModelAdmin):
    pass
