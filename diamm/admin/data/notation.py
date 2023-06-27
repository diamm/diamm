from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.notation import Notation


@admin.register(Notation)
class NotationAdmin(VersionAdmin):
    search_fields = ('name',)
