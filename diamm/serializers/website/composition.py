import re

import ypres
from django.conf import settings
from django.db.models.expressions import Exists, OuterRef
from django.template.loader import get_template
from rest_framework.reverse import reverse

from diamm.helpers.solr_helpers import SolrManager
from diamm.models import Page, SourceURL


class CompositionBibliographySerializer(ypres.DictSerializer):
    pk = ypres.IntField()
    citation = ypres.MethodField()
    pages = ypres.StrField(required=False)
    notes = ypres.StrField(required=False)

    def get_citation(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj["citation_json"])
        # strip out any newlines from the templating process
        citation = re.sub("\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class CompositionCycleCompositionSerializer(ypres.Serializer):
    title = ypres.StrField(attr="composition.title")
    url = ypres.MethodField()

    def get_url(self, obj):
        return reverse(
            "composition-detail",
            kwargs={"pk": obj.composition.pk},
            request=self.context["request"],
        )


class CompositionCycleSerializer(ypres.Serializer):
    title = ypres.StrField(attr="cycle.title")
    type = ypres.StrField(attr="cycle.type.name")
    compositions = ypres.MethodField()

    def get_compositions(self, obj):
        return CompositionCycleCompositionSerializer(
            obj.cycle.compositions.all(),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many


class CompositionContributionSerializer(ypres.Serializer):
    contributor = ypres.StrField(attr="contributor.username")

    summary = ypres.StrField()
    updated = ypres.StrField()


class CompositionSourceSerializer(ypres.Serializer):
    url = ypres.MethodField()
    display_name = ypres.StrField(attr="source.display_name")

    has_images = ypres.MethodField()
    has_external_manifest = ypres.MethodField()
    public_images = ypres.BoolField(attr="source.public_images")
    folio_start = ypres.StrField(required=False)
    folio_end = ypres.StrField(required=False)
    voices = ypres.MethodField()

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
            return CompositionSourceVoiceSerializer(obj.voices.all(), many=True).serialized_many
        return None


class CompositionSourceVoiceSerializer(ypres.Serializer):
    voice_text = ypres.StrField(required=False)
    clef = ypres.StrField(required=False)
    mensuration = ypres.StrField(required=False)
    voice_type = ypres.StrField(required=False, attr="type")
    position = ypres.StrField(required=False)


class CompositionComposerSerializer(ypres.Serializer):
    url = ypres.MethodField()
    full_name = ypres.StrField(attr="composer.full_name")
    uncertain = ypres.BoolField()
    notes = ypres.StrField()

    def get_url(self, obj):
        return reverse(
            "person-detail",
            kwargs={"pk": obj.composer.pk},
            request=self.context["request"],
        )

class CompositionNoteSerializer(ypres.Serializer):
    note_type = ypres.StrField()
    note = ypres.StrField()
    atype = ypres.IntField(label="type", attr="type")



class CompositionDetailSerializer(ypres.Serializer):
    anonymous = ypres.BoolField(attr="anonymous", required=False)
    composers = ypres.MethodField()
    sources = ypres.MethodField()
    type = ypres.MethodField()
    pk = ypres.IntField()
    url = ypres.MethodField()
    title = ypres.StrField()
    cycles = ypres.MethodField()
    genres = ypres.MethodField()
    bibliography = ypres.MethodField()
    notes = ypres.MethodField()

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
            ).serialized_many  # type: ignore
        else:
            return []

    def get_composers(self, obj) -> list:
        if obj.composers:
            return CompositionComposerSerializer(
                obj.composers.all(),
                context={"request": self.context["request"]},
                many=True,
            ).serialized_many  # type: ignore
        else:
            return []

    def get_cycles(self, obj):
        if obj.cycles.exists():
            return CompositionCycleSerializer(
                obj.cycles.all(),
                context={"request": self.context["request"]},
                many=True,
            ).serialized_many
        return []

    def get_genres(self, obj) -> list:
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

                reslist.append(CompositionBibliographySerializer(res).serialized)
        return reslist

    def get_notes(self, obj) -> list:
        if not obj.notes.exists():
            return []

        return CompositionNoteSerializer(obj.notes.all(), many=True).serialized_many
