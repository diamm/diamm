from django.contrib import admin
from diamm.models.data.image import Image
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin


@admin.register(Image)
class ImageAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('legacy_filename', 'get_type')
    list_filter = ("type__name",)
    # filter_horizontal = ('items',)
    search_fields = ('legacy_filename',)

    def get_type(self, obj):
        return "{0}".format(obj.type.name)
    get_type.short_description = "type"
