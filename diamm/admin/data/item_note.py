from django.contrib import admin
from dynamic_raw_id.admin import DynamicRawIDMixin
from reversion.admin import VersionAdmin

from diamm.models.data.item_note import ItemNote


@admin.register(ItemNote)
class ItemNoteAdmin(DynamicRawIDMixin, VersionAdmin):
    list_display = ('get_source', 'note_type')
    dynamic_raw_id_fields = ('item',)

    def get_source(self, obj):
        return f"{obj.item.source.display_name}"
    get_source.short_description = "Source"

