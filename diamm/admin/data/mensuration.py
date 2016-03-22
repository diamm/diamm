from django.contrib import admin
from diamm.models.data.mensuration import Mensuration


@admin.register(Mensuration)
class MensurationAdmin(admin.ModelAdmin):
    list_display = ('sign','text')
