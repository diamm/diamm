from django.contrib import admin
from django.db import models
from diamm.models.data.text import Text
from reversion.admin import VersionAdmin
from pagedown.widgets import AdminPagedownWidget


@admin.register(Text)
class TextAdmin(VersionAdmin):
    list_display = ('incipit',)
    search_fields = ('incipit', 'text')

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }
