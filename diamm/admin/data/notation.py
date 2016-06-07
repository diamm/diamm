from django.contrib import admin
from diamm.models.data.notation import Notation


@admin.register(Notation)
class NotationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
