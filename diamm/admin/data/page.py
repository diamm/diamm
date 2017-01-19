from django.contrib import admin
from diamm.models.data.page import Page
from django_extensions.admin import ForeignKeyAutocompleteAdmin


@admin.register(Page)
class PageAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('get_source', 'numeration', 'page_type')
    search_fields = ('source__shelfmark', 'source__name')
    list_editable = ('page_type',)

    related_search_fields = {
        'source': ['shelfmark', 'name', 'pk']
    }

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "source"
