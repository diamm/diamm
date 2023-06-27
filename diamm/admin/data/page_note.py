from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.page_note import PageNote


@admin.register(PageNote)
class PageNoteAdmin(VersionAdmin):
    pass