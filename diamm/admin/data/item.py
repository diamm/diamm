from django.contrib import admin
from django.template.defaultfilters import truncatewords
from diamm.models.data.item import Item
from diamm.models.data.item_bibliography import ItemBibliography
from diamm.models.data.item_note import ItemNote
from reversion.admin import VersionAdmin
from django_extensions.admin import ForeignKeyAutocompleteAdmin


# class AggregateComposerListFilter(admin.SimpleListFilter):
#     title = _('Aggregate Composer')
#     parameter_name = 'aggregate'
#
#     def lookups(self, request, model_admin):
#         """
#             Since we're filtering against null (below) we reverse the values; that is,
#             "True" is that isnull is False, and vice versa. Also note that self.value()
#             only ever spits out strings...
#         """
#         return (
#             ("True", _("No Aggregate Records")),
#             ("False", _("Only Aggregate Records"))
#         )
#
#     def queryset(self, request, queryset):
#         val = self.value()
#         if not val or val == "True":
#             return queryset
#         elif val == "False":
#             return queryset.filter(aggregate_composer__isnull=False)

class ItemNoteInline(admin.TabularInline):
    model = ItemNote
    extra = 0


class BibliographyInline(admin.TabularInline):
    model = ItemBibliography
    extra = 0
    raw_id_fields = ('bibliography',)


@admin.register(Item)
class ItemAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('get_source', 'get_composition', 'get_composers',
                    'folio_start', 'folio_end')
    search_fields = ("source__name", "source__identifiers__identifier",
                     "composition__title")
    # list_filter = (AggregateComposerListFilter,)
    inlines = (BibliographyInline, ItemNoteInline)
    filter_horizontal = ['pages']
    # exclude = ("pages",)

    related_search_fields = {
        "composition": ("title",),
        "source": ("shelfmark",)
    }

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "source"
    get_source.admin_order_field = "source__shelfmark"

    def get_composers(self, obj):
        if obj.composition:
            return "{0}".format(obj.composition.composer_names)

    get_composers.short_description = "composers"
    get_composers.admin_order_field = 'composition__composers__composer__last_name'

    def get_composition(self, obj):
        if obj.composition:
            return truncatewords(obj.composition.title, 10)

    get_composition.short_description = "composition"
    get_composition.admin_order_field = "composition__title"

    def get_queryset(self, request):
        qset = super(ItemAdmin, self).get_queryset(request)
        qset = qset.select_related('source__archive', 'composition').prefetch_related('pages')
        return qset
