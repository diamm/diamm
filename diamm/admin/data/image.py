import httpx
from django import forms
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from diamm.admin.filters.input_filter import InputFilter
from diamm.models.data.image import Image
from diamm.models.data.image_note import ImageNote
from diamm.models.data.page import Page


class ImageAdminForm(forms.ModelForm):
    """
    This limits the choices for the page dropdown to just those pages
    attached to the source. Of course, this causes a problem if the image
    is not connected to the page, since the page is what is attached to the source.
    Remember:

    Image -> Page -> Source

    So if Page is missing, there is no direct relationship to filter on. We default
    therefore to no pages (a queryset of none). This field will be populated
    when the image is attached to a page which is attached to a source.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.page:
            self.fields["page"].queryset = Page.objects.filter(
                source_id=self.instance.page.source.pk
            )
        else:
            self.fields["page"].queryset = Page.objects.none()


class ImageSourceListFilter(admin.SimpleListFilter):
    title = _("Attached to Source")
    parameter_name = "source_attach"

    def lookups(self, request, model_admin):
        return ("True", _("No Source Attached")), ("False", _("Attached to a Source"))

    def queryset(self, request, queryset):
        val = self.value()
        if not val or val == "False":
            return queryset.filter(page__isnull=False)
        elif val == "True":
            return queryset.filter(page__isnull=True)


class IIIFDataListFilter(admin.SimpleListFilter):
    """
    Filters for where a record has a location, but the IIIF response is null.
    """

    title = _("IIIF Info")
    parameter_name = "iiif_info"

    def lookups(self, request, model_admin):
        return ("False", _("No IIIF Description")), ("True", _("IIIF Description"))

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        if val == "True":
            return queryset.filter(
                location__isnull=False, width__isnull=False, height__isnull=False
            )
        elif val == "False":
            return queryset.filter(
                location__isnull=False, width__isnull=True, height__isnull=True
            )


class ImageNoteInline(admin.TabularInline):
    model = ImageNote
    extra = 0


class SourceKeyFilter(InputFilter):
    parameter_name = "source"
    title = "Source Key"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(page__source__id__exact=self.value())


def refetch_iiif_info(modeladmin, request, queryset):
    with httpx.Client() as client:
        for img in queryset:
            location = img.location
            if not location:
                continue

            url: str = f"{settings.DIAMM_IMAGE_SERVER}{location}/info.json"

            r = client.get(
                url,
                headers={
                    "referer": f"https://{settings.HOSTNAME}",
                    "X-DIAMM": settings.DIAMM_IMAGE_KEY,
                    "User-Agent": settings.DIAMM_UA,
                },
                timeout=10,
            )

            if 200 <= r.status_code < 300:
                j = r.json()
                width = j.get("width")
                height = j.get("height")
                img.width = width
                img.height = height

        Image.objects.bulk_update(queryset, ["width", "height"])


refetch_iiif_info.short_description = "Re-Fetch IIIF Image Info"


def make_selected_images_public(modeladmin, request, queryset):
    queryset.update(public=True)


make_selected_images_public.short_description = "Make selected images public"


def make_selected_images_private(modeladmin, request, queryset):
    queryset.update(public=False)


make_selected_images_private.short_description = "Make selected images private"


@admin.register(Image)
class ImageAdmin(VersionAdmin):
    save_on_top = True
    form = ImageAdminForm
    list_display = ("pk", "public", "location", "get_type")
    list_filter = (
        SourceKeyFilter,
        "type__name",
        ImageSourceListFilter,
        IIIFDataListFilter,
        "public",
        "external",
    )

    list_editable = ("public", "location")

    search_fields = (
        "legacy_filename",
        "location",
        "=page__source__id",
        "page__source__shelfmark",
        "page__source__name",
    )

    inlines = (ImageNoteInline,)

    actions = (
        refetch_iiif_info,
        make_selected_images_public,
        make_selected_images_private,
    )

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "80"})},
        models.URLField: {"widget": TextInput(attrs={"size": "160"})},
    }

    def get_type(self, obj) -> str:
        if not obj.type:
            return "[Unattached]"
        return f"{obj.type.name}"

    get_type.short_description = "type"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("type")
