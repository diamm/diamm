from diamm.models.data.source_relationship_type import SourceRelationshipType
from django.contrib import admin


@admin.register(SourceRelationshipType)
class SourceRelationshipTypeAdmin(admin.ModelAdmin):
    pass
