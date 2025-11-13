from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.item_note import ItemNote


@admin.register(ItemNote)
class ItemNoteAdmin(VersionAdmin):
    list_display = ("get_source", "note_type")
    raw_id_fields = ("item",)

    @admin.display(description="Source")
    def get_source(self, obj):
        return f"{obj.item.source.display_name}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("item__source__archive")
