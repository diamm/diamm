from django.contrib import admin
from diamm.models.data.page import Page
from diamm.models.data.image import Image
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin


class ImageInline(admin.StackedInline):
    model = Image
    extra = 0
    template = "admin/diamm_data/page/edit_inline/stacked_imageview.html"


@admin.register(Page)
class PageAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('get_source', 'numeration', 'page_type', 'legacy_id')
    search_fields = ('source__shelfmark', 'source__name', '=source__id')
    list_editable = ('page_type',)
    inlines = [ImageInline]

    related_search_fields = {
        'source': ['shelfmark', 'name', 'pk']
    }

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "source"
