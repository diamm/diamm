from django.contrib import admin
from diamm.models.data.composition import Composition
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.composition_bibliography import CompositionBibliography


class BibliographyInline(admin.TabularInline):
    model = CompositionBibliography
    extra = 0
    raw_id_fields = ('bibliography',)


class ComposerInline(admin.TabularInline):
    model = CompositionComposer
    extra = 0
    raw_id_fields = ('composer',)


@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_composers', 'get_genres')
    search_fields = ('title', 'composers__composer__last_name')
    inlines = (ComposerInline, BibliographyInline)
    list_filter = ('anonymous',)

    def get_composers(self, obj):
        c = "; ".join([c.composer.full_name for c in obj.composers.all()])
        return "{0}".format(c)
    get_composers.short_description = "Composers"
    get_composers.admin_order_field = "composers__composer__last_name"

    def get_genres(self, obj):
        g = ", ".join([g.name for g in obj.genres.all()])
        return "{0}".format(g)
    get_genres.short_description = "Genres"
