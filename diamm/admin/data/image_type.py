from diamm.models.data.image_type import ImageType
from django.contrib import admin


@admin.register(ImageType)
class ImageTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
