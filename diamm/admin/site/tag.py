from django.contrib import admin
from diamm.models.site.tag import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
