from django.contrib import admin
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

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
        return mark_safe(  # noqa: S308
            f'<a href="{instance.identifier_url}">{instance.identifier_url}</a>'
        )

    def get_shelfmark(self, obj):
        return f"{obj.source.archive.siglum} {obj.source.shelfmark}"

    get_shelfmark.short_description = "Name"
    get_shelfmark.admin_order_field = "source__shelfmark"
