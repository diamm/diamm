from django.contrib import admin
from django.db.models import Count
from reversion.admin import VersionAdmin

from diamm.models import Composition
from diamm.models.data.genre import Genre


class CompositionInline(admin.TabularInline):
    model = Composition.genres.through
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Genre)
class GenreAdmin(VersionAdmin):
    list_display = ("name", "composition_count")
    search_fields = ("name",)
    inlines = (CompositionInline,)

    def composition_count(self, obj) -> str:
        return f"{obj.composition_count}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(composition_count=Count("composition"))
