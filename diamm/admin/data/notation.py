from django.contrib import admin
from diamm.models.data.notation import Notation
from reversion.admin import VersionAdmin


@admin.register(Notation)
class NotationAdmin(VersionAdmin):
    search_fields = ('name',)
