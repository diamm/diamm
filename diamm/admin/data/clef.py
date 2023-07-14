from diamm.models.data.clef import Clef
from django.contrib import admin


@admin.register(Clef)
class ClefAdmin(admin.ModelAdmin):
    list_display = ('name',)
