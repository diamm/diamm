from django.contrib import admin
from django.db import models
from diamm.models.data.source_note import SourceNote
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin


@admin.register(SourceNote)
class SourceNoteAdmin(VersionAdmin):
    list_display = ('get_source', 'note_type')
    search_fields = ('source__shelfmark', 'source__name', '=source__id')
    list_filter = ('type',)

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "Source"
