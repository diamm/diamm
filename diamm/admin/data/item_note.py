from django.contrib import admin
from diamm.models.data.item_note import ItemNote
from reversion.admin import VersionAdmin
from salmonella.admin import SalmonellaMixin


@admin.register(ItemNote)
class ItemNoteAdmin(SalmonellaMixin, VersionAdmin):
    list_display = ('get_source', 'note_type')
    salmonella_fields = ('item',)

    def get_source(self, obj):
        return "{0}".format(obj.item.source.display_name)
    get_source.short_description = "Source"

