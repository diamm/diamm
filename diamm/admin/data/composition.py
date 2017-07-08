from django.contrib import admin
from diamm.models.data.composition import Composition
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.item import Item
from diamm.models.data.composition_bibliography import CompositionBibliography
from reversion.admin import VersionAdmin


class BibliographyInline(admin.TabularInline):
    verbose_name = "Composition Bibliography"
    verbose_name_plural = "Composition Bibliographies"
    model = CompositionBibliography
    extra = 0
    raw_id_fields = ('bibliography',)


class ComposerInline(admin.TabularInline):
    model = CompositionComposer
    extra = 0
    raw_id_fields = ('composer',)


class ItemInline(admin.StackedInline):
    model = Item
    extra = 0
    raw_id_fields = ('source', 'composition', 'pages')


@admin.register(Composition)
class CompositionAdmin(VersionAdmin):
    save_on_top = True
    list_display = ('title', 'get_composers', 'appears_in')
    search_fields = ('title', 'composers__composer__last_name')
    inlines = (ComposerInline, BibliographyInline, ItemInline)
    list_filter = ('anonymous', 'genres')

    def get_composers(self, obj):
        c = "; ".join([c.composer.full_name for c in obj.composers.all()])
        return "{0}".format(c)
    get_composers.short_description = "Composers"
    get_composers.admin_order_field = "composers__composer__last_name"

    def get_genres(self, obj):
        g = ", ".join([g.name for g in obj.genres.all()])
        return "{0}".format(g)
    get_genres.short_description = "Genres"

    def appears_in(self, obj):
        if obj.sources.count() == 0:
            return None
        sources = ["<a href='/admin/diamm_data/source/{0}/change'>{1} {2}</a><br />".format(x[0], x[1], x[2]) for x in obj.sources.values_list('source__pk',
                                                                                                         'source__archive__siglum',
                                                                                                         'source__shelfmark')]
        return "".join(sources)
    appears_in.short_descriptino = "Appears in"
    appears_in.allow_tags = True
