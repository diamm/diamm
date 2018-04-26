from django.contrib import admin
from diamm.models.data.cycle import Cycle
from diamm.models.data.composition_cycle import CompositionCycle
from reversion.admin import VersionAdmin
from dynamic_raw_id.admin import DynamicRawIDMixin


class CompositionCycleInline(DynamicRawIDMixin, admin.TabularInline):
    model = CompositionCycle
    verbose_name = "Composition"
    verbose_name_plural = "Compositions"
    extra = 0
    dynamic_raw_id_fields = ('composition',)


@admin.register(Cycle)
class CycleAdmin(VersionAdmin):
    list_display = ('title', 'composer', 'type')
    list_filter = ('type',)
    search_fields = ('title', 'composer__last_name', 'type__name')
    inlines = (CompositionCycleInline,)
