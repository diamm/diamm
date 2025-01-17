from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.item_note import ItemNote


@admin.register(ItemNote)
class ItemNoteAdmin(VersionAdmin):
    list_display = ("get_source", "note_type")
    raw_id_fields = ("item",)

    def get_source(self, obj):
        return f"{obj.item.source.display_name}"

    get_source.short_description = "Source"
