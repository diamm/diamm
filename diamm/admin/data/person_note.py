from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.person_note import PersonNote


@admin.register(PersonNote)
class PersonNoteAdmin(VersionAdmin):
    search_fields = ("person__last_name", "person__first_name", "person__title")
    list_display = ("get_person", "type")
    list_filter = ("type",)
    raw_id_fields = ("person",)

    def get_person(self, obj):
        return f"{obj.person}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("person")
