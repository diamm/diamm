from django.contrib import admin
from django.db import models
from django.forms import TextInput
from reversion.admin import VersionAdmin

from diamm.admin.filters.input_filter import InputFilter
from diamm.models.data.image import Image
from diamm.models.data.page import Page


class ImageInline(admin.StackedInline):
    model = Image
    extra = 0
    template = "admin/diamm_data/page/edit_inline/stacked_imageview.html"

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "80"})},
        models.URLField: {"widget": TextInput(attrs={"size": "160"})},
    }


class SourceKeyFilter(InputFilter):
    parameter_name = "source"
    title = "Source Key"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source__id__exact=self.value())


@admin.register(Page)
class PageAdmin(VersionAdmin):
    save_on_top = True
    raw_id_fields = ("source",)
    list_filter = (SourceKeyFilter, "page_type", "external")
    list_display = ("get_source", "numeration", "page_type", "sort_order")
    search_fields = (
        "source__shelfmark",
        "source__name",
        "source__archive__siglum",
        "=source__id",
    )
    list_editable = ("numeration", "page_type", "sort_order")
    inlines = [ImageInline]

    def get_source(self, obj):
        return f"{obj.source.display_name}"

    get_source.short_description = "source"
