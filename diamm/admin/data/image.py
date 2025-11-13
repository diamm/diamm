from gettext import ngettext

import httpx
from django import forms
from django.conf import settings
from django.contrib import admin, messages
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
        return queryset


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
        return queryset


class ImageNoteInline(admin.TabularInline):
    model = ImageNote
    extra = 0


class SourceKeyFilter(InputFilter):
    parameter_name = "source"
    title = "Source Key"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(page__source__id__exact=self.value())
        return queryset


@admin.action(description="Make selected images public")
def make_selected_images_public(modeladmin, request, queryset):
    queryset.update(public=True)


@admin.action(description="Make selected images private")
def make_selected_images_private(modeladmin, request, queryset):
    queryset.update(public=False)


@admin.register(Image)
class ImageAdmin(VersionAdmin):
    save_on_top = True
    form = ImageAdminForm
    list_display = ("pk", "public", "location", "get_type", "created", "updated")
    readonly_fields = ("width", "height")
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
        "refetch_iiif_info",
        make_selected_images_public,
        make_selected_images_private,
    )

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "80"})},
        models.URLField: {"widget": TextInput(attrs={"size": "160"})},
    }

    @admin.display(description="Type")
    def get_type(self, obj) -> str:
        if not obj.type:
            return "[Unattached]"
        return f"{obj.type.name}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("type")

    def _fetch_info(self, client, url) -> dict | None:
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
            return {"width": width, "height": height}

        return None

    @admin.action(description="Re-Fetch IIIF Image Info")
    def refetch_iiif_info(self, request, queryset):
        failed_urls = []
        with httpx.Client() as client:
            for img in queryset:
                location = img.location
                if not location:
                    continue

                url: str = f"{settings.DIAMM_IMAGE_SERVER}{location}/info.json"
                wh = self._fetch_info(client, url)
                if not wh:
                    failed_urls.append(url)
                    continue

                img.width = wh["width"]
                img.height = wh["height"]

            Image.objects.bulk_update(queryset, ["width", "height"])

        if failed_urls:
            self.message_user(
                request,
                ngettext("%d url failed", "%d urls failed", len(failed_urls))
                % failed_urls,
                messages.WARNING,
            )
        else:
            self.message_user(
                request,
                "%d sources were updated successfully" % queryset,  # noqa: UP031
                messages.SUCCESS,
            )

    def save_model(self, request, obj, form, change):
        if obj.location:
            with httpx.Client() as client:
                url = f"{settings.DIAMM_IMAGE_SERVER}{obj.location}/info.json"
                wh = self._fetch_info(client, url)
                if not wh:
                    self.message_user(
                        request,
                        "Fetching the Width and Height failed",
                        messages.WARNING,
                    )
                else:
                    obj.width = wh["width"]
                    obj.height = wh["height"]
                    self.message_user(
                        request,
                        "Fetching the Width and Height succeeded",
                        messages.SUCCESS,
                    )

        super().save_model(request, obj, form, change)
