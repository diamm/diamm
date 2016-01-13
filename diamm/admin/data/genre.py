from django.contrib import admin
from diamm.models.data.genre import Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
