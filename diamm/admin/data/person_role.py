from django.contrib import admin
from diamm.models.data.person_role import PersonRole
from salmonella.admin import SalmonellaMixin


@admin.register(PersonRole)
class PersonRoleAdmin(SalmonellaMixin, admin.ModelAdmin):
    list_display = ('person', 'role', 'earliest_year', 'latest_year')
    search_fields = ('person__last_name', 'person__first_name', 'role__name')
    salmonella_fields = ('person', 'role')
