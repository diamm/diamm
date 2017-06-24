from django.contrib import admin
from diamm.models.data.source_relationship_type import SourceRelationshipType


@admin.register(SourceRelationshipType)
class SourceRelationshipTypeAdmin(admin.ModelAdmin):
    pass
