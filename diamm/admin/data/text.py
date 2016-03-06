from django.contrib import admin
from diamm.models.data.text import Text


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('incipit',)
    search_fields = ('incipit', 'text')
