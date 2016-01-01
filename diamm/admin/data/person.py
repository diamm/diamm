from django.contrib import admin
from diamm.models.data.person import Person
from diamm.models.data.person_note import PersonNote
from diamm.models.data.organization import Organization
from simple_history.admin import SimpleHistoryAdmin

class PersonNoteInline(admin.TabularInline):
    model = PersonNote
    extra = 1


def migrate_to_organization(modeladmin, request, queryset):
    """
        Migrates a person to an organzation. Also migrates any relationships
        that may point to that person.
    """
    for entity in queryset:
        d = {
            'legacy_id': entity.legacy_id,
            'name': entity.last_name
        }

        o = Organization(**d)
        o.save()

        # delete the original entity.
        entity.delete()

migrate_to_organization.short_description = "Migrate Person to Organization"


@admin.register(Person)
class PersonAdmin(SimpleHistoryAdmin):
    list_display = ('last_name', 'first_name', 'earliest_year', 'latest_year')
    search_fields = ('last_name', 'first_name')
    inlines = (PersonNoteInline,)
    actions = (migrate_to_organization,)
