from django.contrib import admin
from django.db import models
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin

from diamm.models.data.source_note import SourceNote


@admin.register(SourceNote)
class SourceNoteAdmin(VersionAdmin):
    list_display = ("get_source", "note_type")
    search_fields = ("source__shelfmark", "source__name", "=source__id")
    list_filter = ("type",)
    raw_id_fields = ("source",)

    formfield_overrides = {models.TextField: {"widget": AdminPagedownWidget}}

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("source", "source__archive")

    def get_source(self, obj):
        return f"{obj.source.display_name}"

    get_source.short_description = "Source"
