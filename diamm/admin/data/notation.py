from diamm.models.data.notation import Notation
from django.contrib import admin
from reversion.admin import VersionAdmin


@admin.register(Notation)
class NotationAdmin(VersionAdmin):
    search_fields = ('name',)
