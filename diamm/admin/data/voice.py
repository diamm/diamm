from django.contrib import admin
from diamm.models.data.voice import Voice
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin


@admin.register(Voice)
class VoiceAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    def get_queryset(self, request):
        queryset = super(VoiceAdmin, self).get_queryset(request)
        queryset = queryset.select_related('item__composition', 'mensuration', 'type', 'clef')
        return queryset

    list_display = ['item', 'type', 'mensuration', 'clef']
    list_filter = ['type', 'mensuration', 'clef']

    related_search_fields = {
        'type': ('name',),
        'clef': ('name',),
        'mensuration': ('name',),
        'item': ('composition__name', 'source__name', 'source__shelfmark'),
        'standard_text': ('incipit', 'text')
    }
