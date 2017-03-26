from django.contrib import admin
from diamm.models.data.set import Set
from diamm.models.data.set_bibliography import SetBibliography
from reversion.admin import VersionAdmin


class SetBibliographyInline(admin.TabularInline):
    model = SetBibliography
    extra = 0
    raw_id_fields = ('bibliography',)


@admin.register(Set)
class SetAdmin(VersionAdmin):
    list_display = ('cluster_shelfmark', 'set_type')
    list_filter = ('type',)
    inlines = [SetBibliographyInline]
    filter_horizontal = ('sources',)
