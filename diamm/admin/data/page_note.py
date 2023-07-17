from diamm.models.data.page_note import PageNote
from django.contrib import admin
from reversion.admin import VersionAdmin


@admin.register(PageNote)
class PageNoteAdmin(VersionAdmin):
    list_display = ('get_source', 'page', 'type')
    search_fields = ('page__source__shelfmark', 'page__source__name', 'page__source__archive__siglum')
    raw_id_fields = ('page',)

    def get_source(self, obj):
        return f"{obj.page.source.display_name}"
    get_source.short_description = "source"
