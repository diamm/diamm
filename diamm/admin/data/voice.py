from django.contrib import admin
from diamm.models.data.voice import Voice
from salmonella.admin import SalmonellaMixin
from reversion.admin import VersionAdmin


@admin.register(Voice)
class VoiceAdmin(SalmonellaMixin, VersionAdmin):
    save_on_top = True

    def get_queryset(self, request):
        queryset = super(VoiceAdmin, self).get_queryset(request)
        queryset = queryset.select_related('item__composition', 'mensuration', 'type', 'clef')
        return queryset

    list_display = ['item', 'type', 'mensuration', 'clef']
    list_filter = ['type', 'mensuration', 'clef']
    salmonella_fields = ("type", "clef", "mensuration", "item", "standard_text")
