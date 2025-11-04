from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from diamm.models import Item, Source
from diamm.models.data.notation import Notation


class SourceNotationInline(admin.TabularInline):
    model = Source.notations.through
    extra = 0
    can_delete = 0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def attached_to_source(self, obj):
        change_url = reverse("admin:diamm_data_source_change", args=(obj.source.id,))
        return mark_safe(  # noqa: S308
            f'<a href="{change_url}">{obj.source.display_name}</a>'
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related().all()


class ItemNotationInline(admin.TabularInline):
    model = Item
    extra = 0
    can_delete = False
    fields = ("source", "composition")

    def has_add_permission(self, request, obj):
        return False

    def attached_to_item(self, obj):
        change_url = reverse("admin:diamm_data_item_change", args=(obj.item.id,))
        return mark_safe(  # noqa: S308
            f'<a href="{change_url}">{obj.source.display_name}</a>'
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("source__archive").all()


@admin.register(Notation)
class NotationAdmin(VersionAdmin):
    search_fields = ("name",)
    list_display = ("name", "source_count", "item_count")
    inlines = (ItemNotationInline, SourceNotationInline)

    @admin.display(description="Source count")
    def source_count(self, obj) -> str:
        return f"{obj.source_count}"

    @admin.display(description="Item count")
    def item_count(self, obj) -> str:
        return f"{obj.item_count}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(source_count=Count("sources"), item_count=Count("item"))
