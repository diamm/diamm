from django.contrib import admin
from django.db import models
from diamm.models.site.aboutpages import AboutPages
from pagedown.widgets import AdminPagedownWidget


@admin.register(AboutPages)
class AboutPagesAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }
