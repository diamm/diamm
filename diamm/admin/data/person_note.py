from django.contrib import admin
from reversion.admin import VersionAdmin

from diamm.models.data.person_note import PersonNote


@admin.register(PersonNote)
class PersonNoteAdmin(VersionAdmin):
    search_fields = ('person__last_name', 'person__first_name', 'person__title')
    list_filter = ("type",)
