from django.contrib import admin
from diamm.admin.filters.input_filter import InputFilter
from diamm.models.data.page import Page
from diamm.models.data.image import Image
from dynamic_raw_id.admin import DynamicRawIDMixin
from reversion.admin import VersionAdmin


class ImageInline(admin.StackedInline):
    model = Image
    extra = 0
    template = "admin/diamm_data/page/edit_inline/stacked_imageview.html"


class SourceKeyFilter(InputFilter):
    parameter_name = "source"
    title = "Source Key"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source__id__exact=self.value())


@admin.register(Page)
class PageAdmin(DynamicRawIDMixin, VersionAdmin):
    save_on_top = True
    dynamic_raw_id_fields = ("source",)
    list_filter = (
        SourceKeyFilter,
        "page_type"
    )
    list_display = ('get_source', 'numeration', 'page_type', 'sort_order')
    search_fields = ('source__shelfmark', 'source__name', 'source__archive__siglum', '=source__id')
    list_editable = ('numeration', 'page_type', 'sort_order')
    inlines = [ImageInline]

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "source"
