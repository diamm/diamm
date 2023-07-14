from diamm.models.data.voice_type import VoiceType
from django.contrib import admin


@admin.register(VoiceType)
class VoiceTypeAdmin(admin.ModelAdmin):
    search_fields = ('name',)
