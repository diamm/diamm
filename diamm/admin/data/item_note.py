from django.contrib import admin
from diamm.models.data.item_note import ItemNote
from reversion.admin import VersionAdmin
from dynamic_raw_id.admin import DynamicRawIDMixin


@admin.register(ItemNote)
class ItemNoteAdmin(DynamicRawIDMixin, VersionAdmin):
    list_display = ('get_source', 'note_type')
    dynamic_raw_id_fields = ('item',)

    def get_source(self, obj):
        return "{0}".format(obj.item.source.display_name)
    get_source.short_description = "Source"

