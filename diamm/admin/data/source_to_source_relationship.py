from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.admin.helpers.source_picker import (
    SourceRelationshipAutocompleteSelect,
    source_relationship_picker_label,
)
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name not in self.autocomplete_fields:
            return field

        field.queryset = field.queryset.select_related("archive")
        field.label_from_instance = source_relationship_picker_label
        field.widget = SourceRelationshipAutocompleteSelect(
            db_field.remote_field, self.admin_site, using=kwargs.get("using")
        )
        field.widget.is_required = field.required
        field.widget.choices = field.choices
        return field
