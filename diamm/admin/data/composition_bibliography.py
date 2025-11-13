from django.contrib import admin

from diamm.models.data.composition_bibliography import CompositionBibliography


@admin.register(CompositionBibliography)
class CompositionBibliographyAdmin(admin.ModelAdmin):
    search_fields = (
        "composition__title",
        "bibliography__authors__bibliography_author__last_name",
        "bibliography__abbreviation",
    )
    list_display = ("composition", "bibliography")
    raw_id_fields = ("composition", "bibliography")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("composition", "bibliography").prefetch_related(
            "bibliography__authors__bibliography_author"
        )

        return qs
