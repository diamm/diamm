from django.contrib import admin
from diamm.models.data.page import Page
from diamm.models.data.image import Image
from salmonella.admin import SalmonellaMixin
from reversion.admin import VersionAdmin


class ImageInline(admin.StackedInline):
    model = Image
    extra = 0
    template = "admin/diamm_data/page/edit_inline/stacked_imageview.html"


@admin.register(Page)
class PageAdmin(SalmonellaMixin, VersionAdmin):
    save_on_top = True
    list_display = ('get_source', 'numeration', 'page_type', 'sort_order')
    search_fields = ('source__shelfmark', 'source__name', '=source__id')
    list_editable = ('numeration', 'page_type', 'sort_order')
    inlines = [ImageInline]

    salmonella_fields = ("source",)

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "source"
