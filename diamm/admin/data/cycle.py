from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.composition_cycle import CompositionCycle
from diamm.models.data.cycle import Cycle


class CompositionCycleInline(admin.TabularInline):
    model = CompositionCycle
    verbose_name = "Composition"
    verbose_name_plural = "Compositions"
    extra = 0
    raw_id_fields = ("composition",)


@admin.register(Cycle)
class CycleAdmin(VersionAdmin):
    list_display = ("title", "composer", "type")
    list_filter = ("type",)
    search_fields = ("title", "composer__last_name", "type__name")
    inlines = (CompositionCycleInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("type", "composer")
