from diamm.models.data.organization_type import OrganizationType
from django.contrib import admin


@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    pass
