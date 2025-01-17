from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.mensuration import Mensuration


@admin.register(Mensuration)
class MensurationAdmin(VersionAdmin):
    list_display = ("sign", "text")
    search_fields = ("sign", "text")
