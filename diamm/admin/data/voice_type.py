from django.contrib import admin
from diamm.models.data.voice_type import VoiceType


@admin.register(VoiceType)
class VoiceTypeAdmin(admin.ModelAdmin):
    pass
