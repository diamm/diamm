from django.contrib import admin
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from diamm.models.data.archive_identifier import ArchiveIdentifier


@admin.register(ArchiveIdentifier)
class ArchiveIdentifierAdmin(VersionAdmin):
    search_fields = ("archive__name", "identifier")
    list_display = ("get_archive_name", "identifier_type", "identifier")
    list_filter = ("identifier_type",)
    readonly_fields = ("get_external_url",)
    raw_id_fields = ("archive",)

    def get_archive_name(self, obj):
        return f"{obj.archive.name}"

    get_archive_name.short_description = "Archive"
    get_archive_name.admin_order_field = "archive__name"

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return mark_safe(  # noqa: S308
            f'<a href="{instance.identifier_url}">{instance.identifier_url}</a>'
        )
