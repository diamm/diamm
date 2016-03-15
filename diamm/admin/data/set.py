from django.contrib import admin
from diamm.models.data.set import Set


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ('cluster_shelfmark', 'set_type')
    list_filter = ('type',)
