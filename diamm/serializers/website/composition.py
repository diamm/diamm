import re

import serpy
from django.conf import settings
from django.db.models.expressions import Exists, OuterRef
from django.template.loader import get_template
from rest_framework.reverse import reverse

from diamm.helpers.solr_helpers import SolrManager
from diamm.models import Page, SourceURL
from diamm.serializers.serializers import ContextDictSerializer, ContextSerializer


class CompositionBibliographySerializer(ContextDictSerializer):
    pk = serpy.IntField()
    citation = serpy.MethodField()
    pages = serpy.StrField(required=False)
    notes = serpy.StrField(required=False)

    def get_citation(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj["citation_json"])
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
    has_external_manifest = serpy.MethodField()
    public_images = serpy.BoolField(attr="source.public_images")
    folio_start = serpy.StrField(required=False)
    folio_end = serpy.StrField(required=False)
    voices = serpy.MethodField()

    def get_url(self, obj):
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source.pk},
            request=self.context["request"],
        )

    def get_has_images(self, obj) -> bool:
        return obj.images_are_public

    def get_has_external_manifest(self, obj) -> bool:
        return obj.images_are_public is False and obj.has_manifest_link is True

    def get_voices(self, obj):
        if obj.voices:
            return CompositionSourceVoiceSerializer(obj.voices.all(), many=True).data
        return None


class CompositionSourceVoiceSerializer(ContextSerializer):
    voice_text = serpy.StrField(required=False)
    clef = serpy.StrField(required=False)
    mensuration = serpy.StrField(required=False)
    voice_type = serpy.StrField(required=False, attr="type")
    position = serpy.StrField(required=False)


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

    def get_sources(self, obj) -> list:
        req = self.context["request"]
        public_filter = {} if req.user.is_staff else {"source__public": True}
        if obj.sources:
            return CompositionSourceSerializer(
                obj.sources.select_related("source__archive__city")
                .prefetch_related("voices__type", "voices__clef")
                .filter(**public_filter)
                .annotate(
                    images_are_public=Exists(
                        Page.objects.filter(source=OuterRef("pk"), images__public=True)
                    ),
                    has_manifest_link=Exists(
                        SourceURL.objects.filter(
                            source=OuterRef("pk"), type=SourceURL.IIIF_MANIFEST
                        )
                    ),
                )
                .order_by("source__sort_order"),
                context={"request": self.context["request"]},
                many=True,
            ).data
        else:
            return []

    def get_composers(self, obj) -> list:
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
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = ["type:bibliography", f"compositions_ii:{obj.pk}"]
        sort = "year_ans desc, sort_ans asc"

        connection.search("*:*", fq=fq, sort=sort)
        reslist = []
        for res in connection.results:
            if "compositions_json" in res:
                entry_list = [
                    s
                    for s in res["compositions_json"]
                    if s and s["composition_id"] == obj.pk
                ]
                if not entry_list:
                    continue
                entry = entry_list[0]
                if p := entry.get("pages"):
                    res["pages"] = p
                if n := entry.get("notes"):
                    res["notes"] = n

                reslist.append(CompositionBibliographySerializer(res).data)
        return reslist
