from django.contrib import admin

from diamm.models.data.image_type import ImageType


@admin.register(ImageType)
class ImageTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
