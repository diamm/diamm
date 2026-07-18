from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models import SourceToSourceRelationship


@admin.register(SourceToSourceRelationship)
class SourceToSourceRelationshipAdmin(VersionAdmin):
    list_display = ("from_source", "relationship_type", "to_source")
    list_filter = ("relationship_type",)
    autocomplete_fields = ("from_source", "to_source")
    list_select_related = (
        "from_source__archive",
        "to_source__archive",
        "relationship_type",
    )
