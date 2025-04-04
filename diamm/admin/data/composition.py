from django.contrib import admin, messages
from django.db.models.query import Prefetch
from django.shortcuts import render
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from diamm.admin.forms.assign_genre import AssignGenreForm
from diamm.admin.forms.merge_compositions import MergeCompositionsForm
from diamm.admin.merge_models import merge
from diamm.models.data.composition import Composition
from diamm.models.data.composition_bibliography import CompositionBibliography
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.composition_cycle import CompositionCycle
from diamm.models.data.composition_note import CompositionNote
from diamm.models.data.item import Item


class BibliographyInline(admin.TabularInline):
    verbose_name = "Bibliography"
    verbose_name_plural = "Bibliographies"
    model = CompositionBibliography
    extra = 0
    raw_id_fields = ("bibliography",)


class ComposerInline(admin.TabularInline):
    verbose_name = "Composer"
    verbose_name_plural = "Composers"
    model = CompositionComposer
    extra = 0
    raw_id_fields = ("composer",)


class ItemInline(admin.StackedInline):
    model = Item
    extra = 0
    raw_id_fields = ("source", "pages")
    classes = ["collapse"]


class NoteInline(admin.TabularInline):
    model = CompositionNote
    extra = 0


class CycleInline(admin.StackedInline):
    verbose_name = "Cycle"
    verbose_name_plural = "Cycles"
    model = CompositionCycle
    extra = 0
    raw_id_fields = ("cycle",)


@admin.register(Composition)
class CompositionAdmin(VersionAdmin):
    save_on_top = True
    list_display = ("id", "title", "get_composers", "appears_in", "updated")
    search_fields = ("=id", "title", "composers__composer__last_name")
    inlines = (ComposerInline, NoteInline, CycleInline, BibliographyInline, ItemInline)
    list_filter = ("anonymous", "genres")
    list_editable = ("title",)
    actions = ["merge_compositions_action", "assign_genre_action"]
    readonly_fields = ("created", "updated")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            Prefetch(
                "sources",
                queryset=Item.objects.select_related("source__archive").order_by(
                    "source__archive__siglum", "source__shelfmark"
                ),
            ),
            "composers__composer",
        )

    def get_composers(self, obj):
        c = "; ".join([c.composer.full_name for c in obj.composers.all()])
        return f"{c}"

    get_composers.short_description = "Composers"
    get_composers.admin_order_field = "composers__composer__last_name"

    def get_genres(self, obj):
        g = ", ".join([g.name for g in obj.genres.all()])
        return f"{g}"

    get_genres.short_description = "Genres"

    def appears_in(self, obj) -> str | None:
        if not obj.sources.exists():
            return None

        sources = [
            f"<a href='/admin/diamm_data/source/{x.source.pk}/change'>{x.source.display_name}</a><br />"
            for x in obj.sources.all()
        ]
        return mark_safe("".join(sources))  # noqa: S308

    appears_in.short_description = "Appears in"

    def merge_compositions_action(self, request, queryset):
        if "do_action" in request.POST:
            form = MergeCompositionsForm(request.POST)

            if form.is_valid():
                keep_old = form.cleaned_data["keep_old"]
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

        return render(
            request,
            "admin/composition/merge_compositions.html",
            {"objects": queryset, "form": form},
        )

    merge_compositions_action.short_description = "Merge Compositions"

    def assign_genre_action(self, request, queryset):
        if "do_action" in request.POST:
            form = AssignGenreForm(request.POST)

            if form.is_valid():
                genre = form.cleaned_data["genre"]
                updated = queryset.update(genre=genre)
                messages.success(request, f"{updated} compositions were updated")
            else:
                messages.error(request, "The submitted form was not valid")
        else:
            form = AssignGenreForm()

        return render(
            request,
            "admin/composition/assign_genre.html",
            {"objects": queryset, "form": form},
        )

    assign_genre_action.short_description = "Assign Genre to Compositions"
