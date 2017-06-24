from django.contrib import admin
from diamm.models.data.role import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = ('name',)
