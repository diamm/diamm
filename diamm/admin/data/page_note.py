from django.contrib import admin
from diamm.models.data.page_note import PageNote
from reversion.admin import VersionAdmin


@admin.register(PageNote)
class PageNoteAdmin(VersionAdmin):
    pass