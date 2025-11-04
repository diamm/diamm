from http.client import HTTPResponse

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db import transaction
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
    exclude = ("bibliography_json",)


class NoteInline(admin.TabularInline):
    model = CompositionNote
    extra = 0


class CycleInline(admin.StackedInline):
    verbose_name = "Cycle"
    verbose_name_plural = "Cycles"
    model = CompositionCycle
    extra = 0
    raw_id_fields = ("cycle",)


class CompositionForm(forms.ModelForm):
    class Meta:
        model = Composition
        fields = "__all__"
        widgets = {
            "title": forms.TextInput(attrs={"size": "100"}),  # wider input
        }


@admin.register(Composition)
class CompositionAdmin(VersionAdmin):
    form = CompositionForm

    save_on_top = True
    view_on_site = True
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

    @admin.action(description="Merge Compositions")
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

    @admin.action(description="Assign Genre to Compositions")
    def assign_genre_action(modeladmin, request, queryset):
        # If this is the second step (submitted from our intermediate page)…
        if request.POST.get("do_action"):
            form = AssignGenreForm(request.POST)
            if form.is_valid():
                genre = form.cleaned_data["genre"]
                updated: int = bulk_add_genre_to_queryset(genre, queryset)
                messages.success(request, f"{updated} compositions were updated.")
                # Returning None tells the admin “go back to the changelist”
                return None
            else:
                messages.error(request, "The submitted form was not valid.")
                # fall through to re-render the page with errors
        else:
            # First step: just show the page with the empty form
            form = AssignGenreForm()

        context = {
            "form": form,
            "objects": queryset,
            # needed so the template can preserve the selection on POST
            "action_checkbox_name": ACTION_CHECKBOX_NAME,
            "action_name": "assign_genre_action",
        }
        return render(request, "admin/composition/assign_genre.html", context)


def bulk_add_genre_to_queryset(genre, queryset) -> int:
    through = queryset.model.genres.through
    comp_ids = list(queryset.values_list("id", flat=True))

    # Find which pairs already exist
    existing = set(
        through.objects.filter(
            genre_id=genre.id, composition_id__in=comp_ids
        ).values_list("composition_id", flat=True)
    )

    to_create = [
        through(composition_id=cid, genre_id=genre.id)
        for cid in comp_ids
        if cid not in existing
    ]

    with transaction.atomic():
        # ignore_conflicts requires Django 2.2+
        created = through.objects.bulk_create(to_create, ignore_conflicts=True)

    return len(created)
