from diamm.models.data.source_bibliography import SourceBibliography
from django.contrib import admin


@admin.register(SourceBibliography)
class SourceBibliographyAdmin(admin.ModelAdmin):
    search_fields = ("source__name", "source__identifiers__identifier", "source__shelfmark",
                     'bibliography__authors__bibliography_author__last_name', 'bibliography__abbreviation',
                     "=source__pk")
    list_display = ("get_source", "bibliography")
    list_filter = ("primary_study",)
    raw_id_fields = ('source', 'bibliography')

    def get_source(self, obj):
        return f"{obj.source.display_name}"
    get_source.short_description = "Source"
    get_source.admin_order_field = "source__shelfmark"

