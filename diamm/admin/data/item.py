from django.contrib import admin
from django.template.defaultfilters import truncatewords
from django.utils.translation import ugettext_lazy as _
from diamm.models.data.item import Item
from reversion.admin import VersionAdmin
from django_extensions.admin import ForeignKeyAutocompleteAdmin


class AggregateComposerListFilter(admin.SimpleListFilter):
    title = _('Aggregate Composer')
    parameter_name = 'aggregate'

    def lookups(self, request, model_admin):
        """
            Since we're filtering against null (below) we reverse the values; that is,
            "True" is that isnull is False, and vice versa. Also note that self.value()
            only ever spits out strings...
        """
        return (
            ("True", _("No Aggregate Records")),
            ("False", _("Only Aggregate Records"))
        )

    def queryset(self, request, queryset):
        val = self.value()
        if not val or val == "True":
            return queryset
        elif val == "False":
            return queryset.filter(aggregate_composer__isnull=False)


@admin.register(Item)
class ItemAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('source', 'get_archive_name',
                    'get_composition', 'get_composers',
                    'folio_start', 'folio_end')
    search_fields = ("source__name", "source__identifiers__identifier",
                     "composition__name")
    list_filter = (AggregateComposerListFilter,)

    related_search_fields = {
        "source": ("identifiers__identifier", "name"),
        "composition": ("name",),
        "aggregate_composer": ("last_name",)
    }

    def get_archive_name(self, obj):
        return "{0} ({1})".format(obj.source.archive.name, obj.source.archive.city.name)
    get_archive_name.short_description = "archive"

    def get_composers(self, obj):
        if obj.composition:
            return "{0}".format(obj.composition.composer_names)
        return "{0}".format(obj.aggregate_composer.full_name)
    get_composers.short_description = "composers"
    get_composers.admin_order_field = 'composition__composers__last_name'

    def get_composition(self, obj):
        if obj.composition:
            return truncatewords(obj.composition.name, 10)
        return "Works by {0}".format(obj.aggregate_composer.full_name)
    get_composition.short_description = "composition"
    get_composition.admin_order_field = "composition__name"
