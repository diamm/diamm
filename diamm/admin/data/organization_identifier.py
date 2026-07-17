from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.admin.helpers.html import admin_change_link
from diamm.models.data.organization_identifier import OrganizationIdentifier


@admin.register(OrganizationIdentifier)
class OrganizationIdentifierAdmin(VersionAdmin):
    search_fields = ("organization__name", "identifier")
    # list_display = ('get_organization_name', 'organization__location', 'identifier_type', 'identifier')
    list_filter = ("identifier_type",)
    readonly_fields = ("get_external_url",)
    raw_id_fields = ("organization",)

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return admin_change_link(instance.identifier_url, instance.identifier_url)

    def get_organization_name(self, instance) -> str:
        return f"{instance.organization.name}"
