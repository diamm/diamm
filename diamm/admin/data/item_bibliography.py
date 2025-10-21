from django.contrib import admin

from diamm.models.data.item_bibliography import ItemBibliography


@admin.register(ItemBibliography)
class ItemBibliographyAdmin(admin.ModelAdmin):
    search_fields = (
        "item__source__name",
        "item__source__identifiers__identifier",
        "item__source__shelfmark",
        "bibliography__authors__bibliography_author__last_name",
        "bibliography__abbreviation",
        "=item__pk",
    )
    list_display = ("item", "bibliography")
    raw_id_fields = ("item", "bibliography")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("item__source", "item__composition", "bibliography")

        return qs
