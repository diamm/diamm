from django.contrib import admin
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.person import Person
from diamm.models.data.organization import Organization
from dynamic_raw_id.admin import DynamicRawIDMixin


@admin.register(SourceCopyist)
class SourceCopyistAdmin(DynamicRawIDMixin, admin.ModelAdmin):
    list_display = ('get_source', 'get_copyist', 'copyist_type', 'uncertain')
    list_filter = ('type',)
    dynamic_raw_id_fields = ('source',)

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "source"

    def get_copyist(self, obj):
        if isinstance(obj.copyist, Organization):
            return "{0} (organization)".format(obj.copyist.name)
        elif isinstance(obj.copyist, Person):
            return "{0} (person)".format(obj.copyist.full_name)
        else:
            return None

    get_copyist.short_description = "Related Copyist"

