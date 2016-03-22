from django.contrib import admin
from diamm.models.data.language import Language


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)
