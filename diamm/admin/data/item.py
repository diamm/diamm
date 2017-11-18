from django.contrib import admin
from django.template.defaultfilters import truncatewords
from django.forms import ModelForm
from diamm.models.data.item import Item
from diamm.models.data.page import Page
from diamm.models.data.item_bibliography import ItemBibliography
from diamm.models.data.item_note import ItemNote
from diamm.models.data.item_composer import ItemComposer
from reversion.admin import VersionAdmin
from salmonella.admin import SalmonellaMixin
from django.utils.translation import ugettext_lazy as _


# This custom form will reduce the number of options for the pages to only those
# pages that are linked to the same source.
class ItemAdminForm(ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ItemAdminForm, self).__init__(*args, **kwargs)

        # If we are editing an existing record, show only the pages of the attached source.
        # If we don't have a source attached, show an empty queryset so that no pages show up to add.
        # This helps reduce confusion around what pages are available to add to this item.
        if self.instance.pk:
            self.fields['pages'].queryset = Page.objects.filter(source=self.instance.source).select_related('source').order_by('sort_order')
        else:
            self.fields['pages'].queryset = Page.objects.none()


class ItemNoteInline(admin.TabularInline):
    model = ItemNote
    extra = 0


class BibliographyInline(SalmonellaMixin, admin.TabularInline):
    verbose_name_plural = "Bibliography"
    verbose_name = "Bibliography"
    model = ItemBibliography
    extra = 0
    salmonella_fields = ('bibliography',)


class ItemComposerInline(SalmonellaMixin, admin.TabularInline):
    model = ItemComposer
    extra = 0
    salmonella_fields = ('composer',)


class AttachedToPagesListFilter(admin.SimpleListFilter):
    title = _("Attached to Pages")
    parameter_name = "page_att"

    def lookups(self, request, model_admin):
        return (
            ("False", _("Not attached to pages")),
            ("True", _("Attached to pages"))
        )

    def queryset(self, request, queryset):
        val = self.value()

        if not val:
            return queryset

        if val == "True":
            return queryset.filter(pages__isnull=False)
        elif val == "False":
            return queryset.filter(pages__isnull=True)


@admin.register(Item)
class ItemAdmin(SalmonellaMixin, VersionAdmin):
    save_on_top = True
    form = ItemAdminForm
    list_display = ('get_source', 'get_composition', 'get_composers',
                    'folio_start', 'folio_end', 'pages_attached')
    list_filter = (
        AttachedToPagesListFilter,
    )
    search_fields = ("source__name", "source__identifiers__identifier", "source__shelfmark",
                     "composition__title", "=source__pk")
    # list_filter = (AggregateComposerListFilter,)
    inlines = (ItemNoteInline, ItemComposerInline, BibliographyInline)
    filter_horizontal = ['pages']
    # exclude = ("pages",)
    salmonella_fields = ('source', 'composition')

    def pages_attached(self, obj):
        return obj.pages.count() > 0
    pages_attached.short_description = "Pages Linked"
    pages_attached.boolean = True

    def get_source(self, obj):
        return "{0}".format(obj.source.display_name)
    get_source.short_description = "Source"
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
