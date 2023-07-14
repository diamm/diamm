from diamm.models.data.cycle_type import CycleType
from django.contrib import admin


@admin.register(CycleType)
class CycleTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
