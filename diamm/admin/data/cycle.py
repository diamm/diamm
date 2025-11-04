from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models import CycleComposer
from diamm.models.data.composition_cycle import CompositionCycle
from diamm.models.data.cycle import Cycle


class CompositionCycleInline(admin.TabularInline):
    model = CompositionCycle
    verbose_name = "Composition"
    verbose_name_plural = "Compositions"
    extra = 0
    raw_id_fields = ("composition",)


class CompositionCycleComposersInline(admin.TabularInline):
    model = CycleComposer
    verbose_name = "Composer"
    verbose_name_plural = "Composers"
    extra = 0
    raw_id_fields = ("composer",)


@admin.register(Cycle)
class CycleAdmin(VersionAdmin):
    list_display = ("title", "get_composers", "type")
    list_filter = ("type",)
    search_fields = ("title", "composers__last_name", "type__name")
    inlines = (CompositionCycleInline, CompositionCycleComposersInline)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("composers")
            .select_related("type")
        )

    def get_composers(self, obj):
        c = "; ".join([c.full_name for c in obj.composers.all()])
        return f"{c}"

    get_composers.short_description = "Composers"
    get_composers.admin_order_field = "composers__composer__last_name"
