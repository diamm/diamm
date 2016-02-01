from django.contrib import admin
from django.db import models
from pagedown.widgets import AdminPagedownWidget
from diamm.models.site.story import Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }
