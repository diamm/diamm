from django.contrib import admin
from django.db import models
from diamm.models.data.source_note import SourceNote
from pagedown.widgets import AdminPagedownWidget


@admin.register(SourceNote)
class SourceNoteAdmin(admin.ModelAdmin):
    list_display = ('get_source', 'note_type')
    search_fields = ('source__shelfmark', 'source__name')
    list_filter = ('type',)

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "Source"
