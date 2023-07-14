from diamm.models.data.genre import Genre
from django.contrib import admin
from reversion.admin import VersionAdmin


@admin.register(Genre)
class GenreAdmin(VersionAdmin):
    list_display = ('name',)
    search_fields = ('name',)
