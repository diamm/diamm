from django.contrib import admin
from dynamic_raw_id.admin import DynamicRawIDMixin

from diamm.models.data.person_role import PersonRole


@admin.register(PersonRole)
class PersonRoleAdmin(DynamicRawIDMixin, admin.ModelAdmin):
    list_display = ('person', 'role', 'earliest_year', 'latest_year')
    search_fields = ('person__last_name', 'person__first_name', 'role__name')
    dynamic_raw_id_fields = ('person', 'role')
