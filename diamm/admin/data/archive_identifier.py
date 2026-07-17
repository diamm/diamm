from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.admin.helpers.html import admin_change_link
from diamm.models.data.archive_identifier import ArchiveIdentifier


@admin.register(ArchiveIdentifier)
class ArchiveIdentifierAdmin(VersionAdmin):
    search_fields = ("archive__name", "identifier")
    list_display = ("get_archive_name", "identifier_type", "identifier")
    list_filter = ("identifier_type",)
    readonly_fields = ("get_external_url",)
    raw_id_fields = ("archive",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("archive")

    @admin.display(description="Archive", ordering="archive__name")
    def get_archive_name(self, obj):
        return f"{obj.archive.name}"

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return admin_change_link(instance.identifier_url, instance.identifier_url)
