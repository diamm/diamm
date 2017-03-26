from django.contrib import admin
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.person import Person
from diamm.models.data.organization import Organization
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin


@admin.register(SourceRelationship)
class SourceRelationshipAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('get_source', 'get_related_entity', 'relationship_type')

    # search_fields = ('source__name',
    #                  'source__identifiers__identifier',
    #                  'source__archive__name',
    #                  'person__last_name')
    #
    # related_search_fields = {
    #     'source': ('name', 'identifiers__identifier', 'archive__name'),
    #     'person': ('last_name',)
    # }

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "source"

    def get_related_entity(self, obj):
        if isinstance(obj.related_entity, Organization):
            return "{0} (organization)".format(obj.related_entity.name)
        elif isinstance(obj.related_entity, Person):
            return "{0} (person)".format(obj.related_entity.full_name)
        else:
            return None

    get_related_entity.short_description = "Related Entity"
