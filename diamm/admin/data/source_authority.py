from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.admin.helpers.html import admin_change_link
from diamm.models.data.source_authority import SourceAuthority


@admin.register(SourceAuthority)
class SourceAuthorityAdmin(VersionAdmin):
    search_fields = ("source__shelfmark", "source__archive__name")
    list_display = ("get_shelfmark", "identifier_type", "identifier")
    list_filter = ("identifier_type",)
    readonly_fields = ("get_external_url",)
    # raw_id_fields = ('person',)

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return admin_change_link(instance.identifier_url, instance.identifier_url)

    @admin.display(description="Name", ordering="source__shelfmark")
    def get_shelfmark(self, obj):
        return f"{obj.source.archive.siglum} {obj.source.shelfmark}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("source__archive")
