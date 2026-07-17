from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.admin.helpers.html import admin_change_link
from diamm.models.data.person_identifier import PersonIdentifier


@admin.register(PersonIdentifier)
class PersonIdentifierAdmin(VersionAdmin):
    search_fields = (
        "person__last_name",
        "person__first_name",
        "person__title",
        "identifier",
    )
    list_display = ("get_person_name", "identifier_type", "identifier")
    list_filter = ("identifier_type",)
    readonly_fields = ("get_external_url",)
    raw_id_fields = ("person",)

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return admin_change_link(instance.identifier_url, instance.identifier_url)

    @admin.display(description="Name", ordering="person__last_name")
    def get_person_name(self, obj):
        return f"{obj.person}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("person")
