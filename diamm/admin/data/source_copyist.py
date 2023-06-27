from django.contrib import admin
from dynamic_raw_id.admin import DynamicRawIDMixin

from diamm.models.data.organization import Organization
from diamm.models.data.person import Person
from diamm.models.data.source_copyist import SourceCopyist


@admin.register(SourceCopyist)
class SourceCopyistAdmin(DynamicRawIDMixin, admin.ModelAdmin):
    list_display = ('get_source', 'get_copyist', 'copyist_type', 'uncertain')
    search_fields = ('source__shelfmark', 'source__name', '=source__id')
    list_filter = ('type',)
    dynamic_raw_id_fields = ('source',)

    def get_source(self, obj):
        return f"{obj.source.display_name}"
    get_source.short_description = "source"

    def get_copyist(self, obj):
        if isinstance(obj.copyist, Organization):
            return f"{obj.copyist.name} (organization)"
        elif isinstance(obj.copyist, Person):
            return f"{obj.copyist.full_name} (person)"
        else:
            return None

    get_copyist.short_description = "Related Copyist"
