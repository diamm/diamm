from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.language import Language


@admin.register(Language)
class LanguageAdmin(VersionAdmin):
    list_display = ('name',)
