from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.organization import Organization
from diamm.models.data.person import Person
from diamm.models.data.source_relationship import SourceRelationship


@admin.register(SourceRelationship)
class SourceRelationshipAdmin(VersionAdmin):
    list_display = ("get_source", "get_related_entity", "relationship_type")
    raw_id_fields = ("source",)
    list_filter = ("relationship_type",)

    search_fields = (
        "source__name",
        "source__identifiers__identifier",
        "source__archive__name",
    )
    #
    # related_search_fields = {
    #     'source': ('name', 'identifiers__identifier', 'archive__name'),
    #     'person': ('last_name',)
    # }

    @admin.display(description="Source")
    def get_source(self, obj):
        return f"{obj.source.display_name}"

    @admin.display(description="Related Entity")
    def get_related_entity(self, obj):
        if isinstance(obj.related_entity, Organization):
            return f"{obj.related_entity.name} (organization)"
        elif isinstance(obj.related_entity, Person):
            return f"{obj.related_entity.full_name} (person)"
        return None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "source__archive", "relationship_type", "content_type"
        ).prefetch_related("related_entity")
