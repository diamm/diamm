from diamm.models.data.voice import Voice
from django.contrib import admin
from reversion.admin import VersionAdmin


@admin.register(Voice)
class VoiceAdmin(VersionAdmin):
    save_on_top = True

    def get_queryset(self, request):
        queryset = super(VoiceAdmin, self).get_queryset(request)
        queryset = queryset.select_related('item__composition', 'mensuration', 'type', 'clef')
        return queryset

    list_display = ['item', 'type', 'mensuration', 'clef', 'item_id']
    list_filter = ['type', 'mensuration', 'clef', 'languages']
    search_fields = ('item__composition__title', 'item__source__shelfmark', 'item__source__name', '=item__id')
    raw_id_fields = ("type", "clef", "mensuration", "item", "standard_text")
