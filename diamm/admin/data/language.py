from django.contrib import admin
from diamm.models.data.language import Language
from reversion.admin import VersionAdmin


@admin.register(Language)
class LanguageAdmin(VersionAdmin):
    list_display = ('name',)
