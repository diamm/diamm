from django.contrib import admin

from diamm.models.data.organization_subtype import OrganizationSubtype


@admin.register(OrganizationSubtype)
class OrganizationSubtypeAdmin(admin.ModelAdmin):
    pass
