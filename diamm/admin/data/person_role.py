from django.contrib import admin

from diamm.models.data.person_role import PersonRole


@admin.register(PersonRole)
class PersonRoleAdmin(admin.ModelAdmin):
    list_display = ('person', 'role', 'earliest_year', 'latest_year')
    search_fields = ('person__last_name', 'person__first_name', 'role__name')
    raw_id_fields = ('person', 'role')
