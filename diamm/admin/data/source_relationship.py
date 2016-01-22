from django.contrib import admin
from diamm.models.data.source_relationship import SourceRelationship
from django_extensions.admin import ForeignKeyAutocompleteAdmin


@admin.register(SourceRelationship)
class SourceRelationshipAdmin(ForeignKeyAutocompleteAdmin):
    pass
    # list_display = ('get_source', 'get_person', 'relationship_type')
    # search_fields = ('source__name',
    #                  'source__identifiers__identifier',
    #                  'source__archive__name',
    #                  'person__last_name')
    #
    # related_search_fields = {
    #     'source': ('name', 'identifiers__identifier', 'archive__name'),
    #     'person': ('last_name',)
    # }

    # def get_source(self, obj):
    #     return "{0}".format(obj.source.display_name)
    # get_source.short_description = "source"
    #
    # def get_person(self, obj):
    #     return "{0}".format(obj.person.full_name)
    # get_person.short_description = "person"
