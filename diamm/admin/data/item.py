from django.contrib import admin
from django.db import models
from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.template.defaultfilters import truncatewords
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from diamm.admin.filters.input_filter import InputFilter
from diamm.models import Voice
from diamm.models.data.external_page import ExternalPage
from diamm.models.data.item import Item
from diamm.models.data.item_bibliography import ItemBibliography
from diamm.models.data.item_composer import ItemComposer
from diamm.models.data.item_note import ItemNote
from diamm.models.data.page import Page


class ItemVoice(admin.StackedInline):
    model = Voice
    extra = 0
    autocomplete_fields = ["standard_text"]


# This custom form will reduce the number of options for the pages to only those
# pages that are linked to the same source.
class ItemAdminForm(ModelForm):
    class Meta:
        model = Item
        fields = "__all__"  # noqa: DJ007

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If we are editing an existing record, show only the pages of the attached source.
        # If we don't have a source attached, show an empty queryset so that no pages show up to add.
        # This helps reduce confusion around what pages are available to add to this item.
        if self.instance.pk:
            self.fields["pages"].queryset = (
                Page.objects.filter(source=self.instance.source)
                .select_related("source")
                .order_by("sort_order")
            )
            self.fields["external_pages"].queryset = (
                ExternalPage.objects.filter(source=self.instance.source)
                .select_related("source")
                .order_by("sort_order")
            )
        else:
            self.fields["pages"].queryset = Page.objects.none()
            self.fields["external_pages"].queryset = ExternalPage.objects.none()


class ItemNoteInline(admin.TabularInline):
    model = ItemNote
    extra = 0


class BibliographyInline(admin.TabularInline):
    verbose_name_plural = "Bibliography"
    verbose_name = "Bibliography"
    model = ItemBibliography
    extra = 0
    raw_id_fields = ("bibliography",)
    list_select_related = True


class ItemComposerInline(admin.TabularInline):
    model = ItemComposer
    extra = 0
    raw_id_fields = ("composer",)


class AttachedToPagesListFilter(admin.SimpleListFilter):
    title = _("Attached to Pages")
    parameter_name = "page_att"

    def lookups(self, request, model_admin):
        return (("False", _("Not attached to pages")), ("True", _("Attached to pages")))

    def queryset(self, request, queryset):
        val = self.value()

        if not val:
            return queryset

        if val == "True":
            return queryset.filter(pages__isnull=False)
        elif val == "False":
            return queryset.filter(pages__isnull=True)


class SourceKeyFilter(InputFilter):
    parameter_name = "source"
    title = "Source Key"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source__id__exact=self.value())


class CompositionKeyFilter(InputFilter):
    parameter_name = "composition"
    title = "Composition Key"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(composition__id__exact=self.value())


@admin.register(Item)
class ItemAdmin(VersionAdmin):
    save_on_top = True
    form = ItemAdminForm
    list_display = (
        "get_source",
        "get_composition",
        "get_composers",
        "item_title",
        "folio_start",
        "folio_end",
        "source_order",
        "pages_attached",
        "created",
        "updated",
    )
    list_editable = ("item_title", "source_order", "folio_start", "folio_end")
    list_filter = (
        SourceKeyFilter,
        CompositionKeyFilter,
        AttachedToPagesListFilter,
    )
    search_fields = (
        "source__name",
        "source__identifiers__identifier",
        "source__shelfmark",
        "composition__title",
        "=source__pk",
    )
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "10"})},
    }

    # list_filter = (AggregateComposerListFilter,)
    inlines = (ItemNoteInline, ItemComposerInline, BibliographyInline, ItemVoice)
    filter_horizontal = ["pages"]
    # exclude = ("pages",)
    raw_id_fields = ("source", "composition")

    def pages_attached(self, obj):
        return obj.pages.exists()

    pages_attached.short_description = "Pages Linked"
    pages_attached.boolean = True

    def get_source(self, obj):
        return f"{obj.source.display_name}"

    get_source.short_description = "Source"
    get_source.admin_order_field = "source__shelfmark"

    def get_composers(self, obj):
        if not obj.composition:
            return None

        cnames: list = [c.composer.full_name for c in obj.composition.composers.all()]
        return mark_safe("; <br />".join(cnames))  # noqa: S308

    get_composers.short_description = "Composers"
    get_composers.short_description = "composers"
    get_composers.admin_order_field = "composition__composers__composer__last_name"

    def get_composition(self, obj):
        if obj.composition:
            return truncatewords(obj.composition.title, 10)

    get_composition.short_description = "composition"
    get_composition.admin_order_field = "composition__title"

    def get_queryset(self, request):
        qset = super().get_queryset(request)
        return qset.select_related("source__archive", "composition").prefetch_related(
            "pages", "composition__composers__composer", "voices"
        )
