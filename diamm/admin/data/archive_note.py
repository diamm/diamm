from django.contrib import admin
from diamm.models.data.archive_note import ArchiveNote
from reversion.admin import VersionAdmin


@admin.register(ArchiveNote)
class ArchiveNoteAdmin(VersionAdmin):
    pass
