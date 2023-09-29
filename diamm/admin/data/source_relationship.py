from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.organization import Organization
from diamm.models.data.person import Person
from diamm.models.data.source_relationship import SourceRelationship


@admin.register(SourceRelationship)
class SourceRelationshipAdmin(VersionAdmin):
    list_display = ('get_source', 'get_related_entity', 'relationship_type')
    raw_id_fields = ('source',)
    list_filter = ('relationship_type',)

    search_fields = ('source__name',
                     'source__identifiers__identifier',
                     'source__archive__name')
    #
    # related_search_fields = {
    #     'source': ('name', 'identifiers__identifier', 'archive__name'),
    #     'person': ('last_name',)
    # }

    def get_source(self, obj):
        return f"{obj.source.display_name}"
    get_source.short_description = "source"

    def get_related_entity(self, obj):
        if isinstance(obj.related_entity, Organization):
            return f"{obj.related_entity.name} (organization)"
        elif isinstance(obj.related_entity, Person):
            return f"{obj.related_entity.full_name} (person)"
        else:
            return None

    get_related_entity.short_description = "Related Entity"
