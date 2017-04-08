from django import forms
from django.contrib import admin
from django.conf import settings
import requests
import ujson
from urllib.parse import urljoin
from diamm.models.data.image import Image
from diamm.models.data.image_note import ImageNote
from diamm.models.data.page import Page
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin
from django.utils.translation import ugettext_lazy as _


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
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        if self.instance.page:
            self.fields['page'].queryset = Page.objects.filter(source_id=self.instance.page.source.pk)
        else:
            self.fields['page'].queryset = Page.objects.none()


class ImageSourceListFilter(admin.SimpleListFilter):
    title = _("Attached to Source")
    parameter_name = "source_attach"

    def lookups(self, request, model_admin):
        return (
            ("True", _("No Source Attached")),
            ("False", _("Attached to a Source"))
        )

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
        return (
            ("False", _("No IIIF Description")),
            ("True", _("IIIF Description"))
        )

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        if val == "True":
            return queryset.filter(
                    location__isnull=False,
                    iiif_response_cache__isnull=False)
        elif val == "False":
            return queryset.filter(
                    location__isnull=False,
                    iiif_response_cache__isnull=True)


class ImageNoteInline(admin.TabularInline):
    model = ImageNote
    extra = 0


def refetch_iiif_info(modeladmin, request, queryset):
    for img in queryset:
        location = img.location
        url = urljoin(location + "/", "info.json")

        r = requests.get(url, headers={
            "referer": "https://{0}".format(settings.HOSTNAME),
            "X-DIAMM": settings.DIAMM_IMAGE_KEY
        })

        if 200 <= r.status_code < 300:
            j = r.json()
            img.iiif_response_cache = ujson.dumps(j)
            img.save()

refetch_iiif_info.short_description = "Re-Fetch IIIF Image Info"


@admin.register(Image)
class ImageAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    form = ImageAdminForm
    list_display = ('legacy_filename', 'location', 'get_type', 'public')
    list_filter = ("type__name", ImageSourceListFilter, IIIFDataListFilter, 'public')
    # filter_horizontal = ('items',)
    search_fields = ('legacy_filename',)
    inlines = (ImageNoteInline,)
    actions = (refetch_iiif_info,)

    def get_type(self, obj):
        return "{0}".format(obj.type.name)
    get_type.short_description = "type"
