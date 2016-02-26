from django.contrib import admin
from diamm.models.data.set import Set


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    pass
