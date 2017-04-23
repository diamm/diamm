from django.contrib import admin
from diamm.models.data.archive_note import ArchiveNote
from reversion.admin import VersionAdmin


@admin.register(ArchiveNote)
class ArchiveNoteAdmin(VersionAdmin):
    list_display = ('archive', 'note_type')
    search_fields = ('archive__name',)
