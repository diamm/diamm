from django.contrib import admin

from diamm.models.data.organization_type import OrganizationType


@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    pass
