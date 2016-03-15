from django.contrib import admin
from diamm.models.data.cycle import Cycle
from diamm.models.data.composition_cycle import CompositionCycle


class CompositionCycleInline(admin.TabularInline):
    model = CompositionCycle
    extra = 0
    raw_id_fields = ('composition',)


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('title', 'composer', 'type')
    list_filter = ('type',)
    search_fields = ('title', 'composer__last_name', 'type__name')
    inlines = (CompositionCycleInline,)
