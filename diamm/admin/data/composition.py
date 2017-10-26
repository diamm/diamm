from django.contrib import admin, messages
from django.shortcuts import render
from diamm.models.data.composition import Composition
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.item import Item
from diamm.models.data.composition_bibliography import CompositionBibliography
from diamm.models.data.composition_cycle import CompositionCycle
from diamm.admin.forms.merge_compositions import MergeCompositionsForm
from diamm.admin.forms.assign_genre import AssignGenreForm
from diamm.admin.merge_models import merge
from salmonella.admin import SalmonellaMixin
from reversion.admin import VersionAdmin


class BibliographyInline(SalmonellaMixin, admin.TabularInline):
    verbose_name = "Bibliography"
    verbose_name_plural = "Bibliographies"
    model = CompositionBibliography
    extra = 0
    salmonella_fields = ('bibliography',)


class ComposerInline(SalmonellaMixin, admin.TabularInline):
    verbose_name = "Composer"
    verbose_name_plural = "Composers"
    model = CompositionComposer
    extra = 0
    salmonella_fields = ('composer',)


class ItemInline(SalmonellaMixin, admin.StackedInline):
    model = Item
    extra = 0
    salmonella_fields = ('source', 'pages')
    classes = ['collapse']


class CycleInline(SalmonellaMixin, admin.StackedInline):
    verbose_name = "Cycle"
    verbose_name_plural = "Cycles"
    model = CompositionCycle
    extra = 0
    salmonella_fields = ('cycle',)


@admin.register(Composition)
class CompositionAdmin(VersionAdmin):
    save_on_top = True
    list_display = ('title', 'get_composers', 'appears_in', 'id')
    search_fields = ('=id', 'title', 'composers__composer__last_name')
    inlines = (ComposerInline, CycleInline, BibliographyInline, ItemInline)
    list_filter = ('anonymous', 'genres')
    actions = ["merge_compositions_action", "assign_genre_action"]

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
    appears_in.short_description = "Appears in"
    appears_in.allow_tags = True

    def merge_compositions_action(self, request, queryset):
        if 'do_action' in request.POST:
            form = MergeCompositionsForm(request.POST)

            if form.is_valid():
                keep_old = form.cleaned_data['keep_old']
                target = queryset.first()
                remainder = list(queryset[1:])
                merged = merge(target, remainder, keep_old=keep_old)

                # Trigger saves for solr
                # for relationship in merged.
                for relationship in merged.composers.all():
                    relationship.save()

                for relationship in merged.sources.all():
                    relationship.save()

                for relationship in merged.bibliography.all():
                    relationship.save()

                messages.success(request, "Objects successfully merged")
                return
            else:
                messages.error(request, "There was an error merging these compositions")
        else:
            form = MergeCompositionsForm()

        return render(request,
                      'admin/composition/merge_compositions.html', {
                        'objects': queryset,
                        'form': form
                      })
    merge_compositions_action.short_description = "Merge Compositions"

    def assign_genre_action(self, request, queryset):
        if 'do_action' in request.POST:
            form = AssignGenreForm(request.POST)

            if form.is_valid():
                genre = form.cleaned_data['genre']
                updated = queryset.update(genre=genre)
                messages.success(request, "{0} compositions were updated".format(updated))
            else:
                messages.error(request, "The submitted form was not valid")
        else:
            form = AssignGenreForm()

        return render(request,
                      'admin/composition/assign_genre.html', {
                        'objects': queryset,
                        'form': form
                      })
    assign_genre_action.short_description = "Assign Genre to Compositions"
