from django.contrib import admin
from diamm.models.site.cover_image import CoverImage


@admin.register(CoverImage)
class CoverImageAdmin(admin.ModelAdmin):
    pass
