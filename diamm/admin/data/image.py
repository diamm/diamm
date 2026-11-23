from dataclasses import asdict, replace
from datetime import timedelta
from gettext import ngettext
from urllib.parse import quote, urlencode

import requests
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q, QuerySet
from django.forms import TextInput
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseBase,
    HttpResponseNotAllowed,
)
from django.shortcuts import get_object_or_404, redirect
from django.tasks import TaskResultStatus, task_backends
from django.tasks.exceptions import TaskResultDoesNotExist
from django.template.response import TemplateResponse
from django.urls import URLPattern, path, reverse
from django.utils.translation import gettext_lazy as _
from pyreqwest.client import SyncClient, SyncClientBuilder
from pyreqwest.exceptions import PyreqwestError, StatusError
from reversion.admin import VersionAdmin

from diamm.admin.filters.input_filter import InputFilter
from diamm.admin.forms.rotate_images import RotationForm
from diamm.imageops.jobs import QueuedRotation, enqueue_rotations, selection_for
from diamm.models.data.image import Image
from diamm.models.data.image_note import ImageNote
from diamm.models.data.page import Page

IIIF_INFO_CLIENT: SyncClient = (
    SyncClientBuilder().connect_timeout(timedelta(seconds=2)).build()
)


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

    def __init__(self, *args: object, **kwargs: object) -> None:
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

    def lookups(
        self, request: HttpRequest, model_admin: type[admin.ModelAdmin]
    ) -> tuple[tuple[str, str], tuple[str, str]]:
        return ("True", _("No Source Attached")), ("False", _("Attached to a Source"))

    def queryset(self, request: HttpRequest, queryset):
        val = self.value()
        if not val:
            return queryset
        if val == "False":
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

    def lookups(
        self, request: HttpRequest, model_admin: type[admin.ModelAdmin]
    ) -> tuple[tuple[str, str], tuple[str, str]]:
        return ("False", _("No IIIF Description")), ("True", _("IIIF Description"))

    def queryset(self, request: HttpRequest, queryset):
        val = self.value()
        if not val:
            return queryset
        if val == "True":
            return queryset.filter(
                location__isnull=False, width__isnull=False, height__isnull=False
            )
        elif val == "False":
            return queryset.filter(location__isnull=False).filter(
                Q(width__isnull=True) | Q(height__isnull=True)
            )
        return queryset


class ImageNoteInline(admin.TabularInline):
    model = ImageNote
    extra = 0


class SourceKeyFilter(InputFilter):
    parameter_name = "source"
    title = "Source Key"

    def queryset(self, request: HttpRequest, queryset):
        if self.value():
            return queryset.filter(page__source__id__exact=self.value())
        return queryset


@admin.action(description="Make selected images public")
def make_selected_images_public(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset
) -> None:
    queryset.update(public=True)


@admin.action(description="Make selected images private")
def make_selected_images_private(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset
) -> None:
    queryset.update(public=False)


STATUS_SALT = "diamm.imageops.status"


class ImageRotationAdminMixin(admin.ModelAdmin):
    """Image rotation routes, confirmation, progress and authenticated previews."""

    rotation_form_class: type[forms.Form]

    def get_urls(self) -> list[URLPattern]:
        return [
            path(
                "rotation/status/",
                self.admin_site.admin_view(self.rotation_status),
                name="diamm_data_image_rotation_status",
            ),
            path(
                "<int:image_id>/rotation-preview/",
                self.admin_site.admin_view(self.rotation_preview),
                name="diamm_data_image_rotation_preview",
            ),
        ] + super().get_urls()

    @admin.action(description="Rotate images", permissions=["change"])
    def rotate_images(
        self, request: HttpRequest, queryset: QuerySet[Image]
    ) -> HttpResponseBase:
        if not self.has_change_permission(request):
            raise PermissionDenied
        remove_image = request.POST.get("remove_image", "")
        if remove_image.isdecimal():
            queryset = queryset.exclude(pk=remove_image)
        selected = [selection_for(image) for image in queryset.order_by("pk")]
        form = self.rotation_form_class(
            request.POST if "apply_rotation" in request.POST or "remove_image" in request.POST else None,
        )
        if "apply_rotation" in request.POST and form.is_valid():
            submitted = enqueue_rotations(queryset, form.cleaned_data["rotation"])
            self.message_user(request, "Rotation request recorded. Missing or unavailable files were not queued.", messages.INFO)
            token = signing.dumps([asdict(row) for row in submitted], salt=STATUS_SALT, compress=True)
            return redirect(
                f"{reverse('admin:diamm_data_image_rotation_status')}?{urlencode({'tasks': token})}"
            )
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Rotate images",
            "form": form,
            "selected": selected,
            "action_checkbox_name": ACTION_CHECKBOX_NAME,
        }
        return TemplateResponse(request, "admin/diamm_data/image/rotate.html", context)

    def rotation_status(self, request: HttpRequest) -> HttpResponseBase:
        if not self.has_change_permission(request):
            raise PermissionDenied
        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])
        try:
            submitted = signing.loads(request.GET.get("tasks", ""), salt=STATUS_SALT)
        except signing.BadSignature:
            return HttpResponseBadRequest("Invalid rotation status link.")
        operations: list[QueuedRotation] = []
        pending = False
        for values in submitted:
            operation = QueuedRotation(**values)
            if not operation.task_id:
                operations.append(operation)
                continue
            try:
                result = task_backends["default"].get_result(operation.task_id)
            except TaskResultDoesNotExist:
                operation = replace(operation, status="Unavailable", message="Task result has been removed.")
            else:
                pending |= not result.is_finished
                status = {
                    TaskResultStatus.READY: "Waiting",
                    TaskResultStatus.RUNNING: "Working",
                    TaskResultStatus.SUCCESSFUL: "Done",
                    TaskResultStatus.FAILED: "Error",
                }[result.status]
                message = ""
                if result.status == TaskResultStatus.SUCCESSFUL:
                    message = result.return_value["message"]
                elif result.errors:
                    message = result.errors[-1].traceback.strip().splitlines()[-1]
                operation = replace(operation, status=status, message=message)
            operations.append(operation)
        return TemplateResponse(
            request, "admin/diamm_data/image/rotation_status.html",
            {
                **self.admin_site.each_context(request),
                "opts": self.model._meta,
                "title": "Image rotation status",
                "operations": operations, "pending": pending,
            },
        )

    def rotation_preview(self, request: HttpRequest, image_id: int) -> HttpResponse:
        if not self.has_change_permission(request):
            raise PermissionDenied
        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])
        image = get_object_or_404(self.get_queryset(request), pk=image_id)
        if image.external or not image.location:
            return HttpResponse("No local image preview.", status=404)
        # Fetch a fixed-size JPEG from the trusted internal IIP server rather
        # than exposing a server-only address to the browser.
        location = quote(image.location, safe="/")
        url = f"{settings.DIAMM_IMAGE_SERVER}{location}/full/!240,240/0/default.jpg"
        headers = {"referer": f"https://{settings.HOSTNAME}"}
        if image_key := getattr(settings, "DIAMM_IMAGE_KEY", None):
            headers["X-DIAMM"] = image_key
        try:
            with requests.get(
                url, headers=headers, timeout=(3, 15), stream=True, allow_redirects=False
            ) as response:
                response.raise_for_status()
                if response.status_code != 200 or response.headers.get("Content-Type", "").split(";")[0] != "image/jpeg":
                    return HttpResponse("Preview server did not return a JPEG.", status=502)
                chunks: list[bytes] = []
                size = 0
                for chunk in response.iter_content(65536):
                    size += len(chunk)
                    if size > 5_000_000:
                        return HttpResponse("Preview is too large.", status=502)
                    chunks.append(chunk)
        except requests.RequestException:
            return HttpResponse("Image preview is unavailable.", status=502)
        return HttpResponse(b"".join(chunks), content_type="image/jpeg")


@admin.register(Image)
class ImageAdmin(ImageRotationAdminMixin, VersionAdmin):
    save_on_top = True
    form = ImageAdminForm
    rotation_form_class = RotationForm
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
        "rotate_images",
        "refetch_iiif_info",
        make_selected_images_public,
        make_selected_images_private,
    )

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "80"})},
        models.URLField: {"widget": TextInput(attrs={"size": "160"})},
    }

    @admin.display(description="Type")
    def get_type(self, obj: Image) -> str:
        if not obj.type:
            return "[Unattached]"
        return f"{obj.type.name}"

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        return qs.select_related("type")

    def _fetch_info(self, client: SyncClient, url: str) -> dict[str, int | None] | None:
        try:
            response = (
                client.get(url)
                .headers(
                    {
                        "referer": f"https://{settings.HOSTNAME}",
                        "X-DIAMM": settings.DIAMM_IMAGE_KEY,
                        "User-Agent": settings.DIAMM_UA,
                    }
                )
                .timeout(timedelta(seconds=10))
                .build()
                .send()
            )
            response.error_for_status()
            j = response.json()
            width = j.get("width")
            height = j.get("height")
            return {"width": width, "height": height}
        except (PyreqwestError, StatusError):
            return None

    @admin.action(description="Re-Fetch IIIF Image Info")
    def refetch_iiif_info(self, request: HttpRequest, queryset) -> None:
        failed_urls: list[str] = []
        success_urls: list[str] = []
        updated_images: list[Image] = []
        for img in queryset:
            location = img.location
            if not location:
                continue

            url: str = f"{settings.DIAMM_IMAGE_SERVER}{location}/info.json"
            wh = self._fetch_info(IIIF_INFO_CLIENT, url)
            if not wh:
                failed_urls.append(url)
                continue
            success_urls.append(url)

            img.width = wh["width"]
            img.height = wh["height"]
            updated_images.append(img)

        if updated_images:
            Image.objects.bulk_update(updated_images, ["width", "height"])

        if failed_urls:
            self.message_user(
                request,
                ngettext("%d url failed", "%d urls failed", len(failed_urls))
                % len(failed_urls),
                messages.WARNING,
            )
        else:
            self.message_user(
                request,
                ngettext(
                    "%d image was updated successfully",
                    "%d images were updated successfully",
                    len(success_urls),
                )
                % len(success_urls),
                messages.SUCCESS,
            )

    def save_model(
        self,
        request: HttpRequest,
        obj: Image,
        form: forms.ModelForm,
        change: bool,
    ) -> None:
        if obj.location:
            url = f"{settings.DIAMM_IMAGE_SERVER}{obj.location}/info.json"
            wh = self._fetch_info(IIIF_INFO_CLIENT, url)
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
