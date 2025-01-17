from django.contrib import admin

from diamm.models.data.clef import Clef


@admin.register(Clef)
class ClefAdmin(admin.ModelAdmin):
    list_display = ("name",)
