from django.contrib import admin

from diamm.models.data.cycle_type import CycleType


@admin.register(CycleType)
class CycleTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
