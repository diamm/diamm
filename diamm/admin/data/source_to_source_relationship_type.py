from django.contrib import admin

from diamm.models import SourceToSourceRelationshipType


@admin.register(SourceToSourceRelationshipType)
class SourceToSourceRelationshipTypeAdmin(admin.ModelAdmin):
    list_display = ("forward_label", "inverse_label")
    search_fields = ("forward_label", "inverse_label")
