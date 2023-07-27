from django.contrib import admin
from django.db import models
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin

from diamm.models.data.set import Set
from diamm.models.data.set_bibliography import SetBibliography


class SetBibliographyInline(admin.TabularInline):
    model = SetBibliography
    extra = 0
    raw_id_fields = ('bibliography',)


@admin.register(Set)
class SetAdmin(VersionAdmin):
    save_on_top = True
    list_display = ('cluster_shelfmark', 'set_type')
    list_filter = ('type',)
    search_fields = ('cluster_shelfmark', 'sources__shelfmark', 'sources__name')
    inlines = [SetBibliographyInline]
    filter_horizontal = ('sources',)

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }
