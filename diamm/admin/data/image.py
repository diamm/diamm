from django.contrib import admin
from diamm.models.data.image import Image
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin


@admin.register(Image)
class ImageAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('filename', 'get_sources', 'get_type', 'get_digitized')
    list_filter = ("type__name", "conditions__condition")
    # filter_horizontal = ('items',)
    raw_id_fields = ('items',)
    search_fields = ('items__source__identifiers__identifier',)

    related_search_fields = {
        'items': ("composition__name",)
    }

    def get_type(self, obj):
        return "{0}".format(obj.type.name)
    get_type.short_description = "type"

    def get_digitized(self, obj):
        return obj.digitized
    get_digitized.short_description = 'digitized'
    get_digitized.boolean = True

    def get_sources(self, obj):
        return "{0}".format(obj.sources)
    get_sources.short_description = "sources"
