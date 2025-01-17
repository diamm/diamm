import re

import serpy
from django.template.loader import get_template
from rest_framework.reverse import reverse

from diamm.serializers.serializers import ContextSerializer


class CompositionBibliographySerializer(ContextSerializer):
    citation = serpy.MethodField()
    pages = serpy.StrField()

    def get_citation(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj.bibliography)
        # strip out any newlines from the templating process
        citation = re.sub("\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class CompositionCycleCompositionSerializer(ContextSerializer):
    title = serpy.StrField(attr="composition.title")
    url = serpy.MethodField()

    def get_url(self, obj):
        return reverse(
            "composition-detail",
            kwargs={"pk": obj.composition.pk},
            request=self.context["request"],
        )


class CompositionCycleSerializer(ContextSerializer):
    title = serpy.StrField(attr="cycle.title")
    type = serpy.StrField(attr="cycle.type.name")
    compositions = serpy.MethodField()

    def get_compositions(self, obj):
        return CompositionCycleCompositionSerializer(
            obj.cycle.compositions.all(),
            many=True,
            context={"request": self.context["request"]},
        ).data


class CompositionContributionSerializer(ContextSerializer):
    contributor = serpy.StrField(attr="contributor.username")

    summary = serpy.StrField()
    updated = serpy.StrField()


class CompositionSourceSerializer(ContextSerializer):
    url = serpy.MethodField()
    display_name = serpy.StrField(attr="source.display_name")

    has_images = serpy.MethodField()

    public_images = serpy.BoolField(attr="source.public_images")
    folios = serpy.MethodField()

    def get_folios(self, obj):
        folio_start = obj.folio_start
        folio_end = obj.folio_end

        folios = ""

        if folio_start:
            folios += f"{folio_start}"

        if folio_end and folio_start != folio_end:
            folios += f"—{folio_end}"

        return folios

    def get_url(self, obj):
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source.pk},
            request=self.context["request"],
        )

    def get_has_images(self, obj):
        return obj.pages.exists()


class CompositionComposerSerializer(ContextSerializer):
    url = serpy.MethodField()
    full_name = serpy.StrField(attr="composer.full_name")
    uncertain = serpy.BoolField()
    notes = serpy.StrField()

    def get_url(self, obj):
        return reverse(
            "person-detail",
            kwargs={"pk": obj.composer.pk},
            request=self.context["request"],
        )


class CompositionDetailSerializer(ContextSerializer):
    anonymous = serpy.BoolField(attr="anonymous", required=False)
    composers = serpy.MethodField()
    sources = serpy.MethodField()
    type = serpy.MethodField()
    pk = serpy.IntField()
    url = serpy.MethodField()
    title = serpy.StrField()
    cycles = serpy.MethodField()
    genres = serpy.MethodField()
    bibliography = serpy.MethodField()

    def get_url(self, obj):
        return reverse(
            "composition-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_sources(self, obj):
        if obj.sources:
            return CompositionSourceSerializer(
                obj.sources.all().order_by("source__sort_order"),
                context={"request": self.context["request"]},
                many=True,
            ).data
        else:
            return []

    def get_composers(self, obj):
        if obj.composers:
            return CompositionComposerSerializer(
                obj.composers.all(),
                context={"request": self.context["request"]},
                many=True,
            ).data
        else:
            return []

    def get_cycles(self, obj):
        if obj.cycles.exists():
            return CompositionCycleSerializer(
                obj.cycles.all(),
                context={"request": self.context["request"]},
                many=True,
            ).data
        return []

    def get_genres(self, obj):
        if obj.genres.exists():
            return [g.name for g in obj.genres.all()]
        return []

    def get_bibliography(self, obj):
        return CompositionBibliographySerializer(obj.bibliography.all(), many=True).data
