from django.contrib import admin
from django.db import models
from diamm.models.data.source_note import SourceNote
from django.utils.translation import ugettext_lazy as _
from pagedown.widgets import AdminPagedownWidget


class NoteTypeListFilter(admin.SimpleListFilter):
    title = _('Note Type')
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return SourceNote.NOTE_TYPES

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(type=self.value())


@admin.register(SourceNote)
class SourceNoteAdmin(admin.ModelAdmin):
    list_display = ('get_source', 'note_type')
    search_fields = ('source__shelfmark', 'source__name')
    list_filter = (NoteTypeListFilter,)

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "Source"
