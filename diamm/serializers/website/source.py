import re

import serpy
from django.conf import settings
from django.contrib.contenttypes.prefetch import GenericPrefetch
from django.db.models.functions.comparison import Collate
from django.template.loader import get_template
from rest_framework.reverse import reverse

from diamm.helpers.solr_helpers import SolrManager
from diamm.models import Organization, Person
from diamm.serializers.fields import DateTimeField
from diamm.serializers.serializers import ContextDictSerializer, ContextSerializer


class SourceCatalogueEntrySerializer(ContextSerializer):
    entry = serpy.MethodField()
    order = serpy.IntField()

    def get_entry(self, obj) -> str:
        request = self.context["request"]
        return (
            f"{request.scheme}://{request.get_host()}/media/rism/catalogue/{obj.entry}"
        )


class SourceCopyistSerializer(ContextSerializer):
    copyist = serpy.MethodField()
    uncertain = serpy.BoolField(attr="uncertain", required=False)
    type = serpy.StrField(attr="get_type_display", call=True)
    type_s = serpy.StrField(attr="get_type_display", call=True)

    def get_copyist(self, obj) -> dict:
        content_type = None
        if obj.content_type_id == 37:
            content_type = "person"
        elif obj.content_type_id == 52:
            content_type = "organization"

        if content_type is not None:
            url = reverse(
                f"{content_type}-detail",
                kwargs={"pk": obj.object_id},
                request=self.context["request"],
            )
            return {"name": str(obj.copyist), "url": url}
        else:
            return {"name": str(obj.copyist)}


class SourceRelationshipSerializer(ContextSerializer):
    related_entity = serpy.MethodField()
    uncertain = serpy.BoolField(attr="uncertain", required=False)
    relationship_type = serpy.StrField(attr="relationship_type")

    def get_related_entity(self, obj):
        content_type = None
        if obj.content_type_id == 37:
            content_type = "person"
        elif obj.content_type_id == 52:
            content_type = "organization"

        if content_type is not None:
            url = reverse(
                f"{content_type}-detail",
                kwargs={"pk": obj.object_id},
                request=self.context["request"],
            )
            return {"name": str(obj.related_entity), "url": url}
        else:
            return {"name": str(obj.related_entity)}


class SourceProvenanceSerializer(ContextSerializer):
    city = serpy.StrField(attr="city.name", required=False)
    country = serpy.StrField(attr="country.name", required=False)
    region = serpy.StrField(attr="region.name", required=False)
    protectorate = serpy.StrField(attr="protectorate.name", required=False)
    entity = serpy.MethodField()
    country_uncertain = serpy.BoolField(attr="country_uncertain")
    city_uncertain = serpy.BoolField(attr="city_uncertain")
    entity_uncertain = serpy.BoolField(attr="entity_uncertain")
    region_uncertain = serpy.BoolField(attr="region_uncertain")

    def get_entity(self, obj):
        if not obj.entity:
            return None

        content_type = None
        if obj.content_type_id == 37:
            content_type = "person"
        elif obj.content_type_id == 52:
            content_type = "organization"

        if content_type is not None:
            url = reverse(
                f"{content_type}-detail",
                kwargs={"pk": obj.object_id},
                request=self.context["request"],
            )
            return {"name": str(obj.entity), "url": url}
        return {"name": str(obj.entity)}


class SourceSetSerializer(ContextDictSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    cluster_shelfmark = serpy.StrField(attr="cluster_shelfmark_s")
    set_type = serpy.StrField(attr="set_type_s")
    sources = serpy.MethodField()

    def get_url(self, obj):
        return reverse(
            "set-detail", kwargs={"pk": obj["pk"]}, request=self.context["request"]
        )

    def get_sources(self, obj) -> list:
        sources = obj["sources_json"]
        ret = []
        for source in sources:
            url = reverse(
                "source-detail",
                kwargs={
                    "pk": source["pk"],
                },
                request=self.context["request"],
            )
            if c := source.get("cover_image"):
                cover = reverse(
                    "cover-image",
                    kwargs={"pk": c},
                    request=self.context["request"],
                )
            else:
                cover = None

            ret.append(
                {
                    "display_name": source["display_name"],
                    "url": url,
                    "cover_image": cover,
                }
            )

        return ret


class SourceBibliographySerializer(ContextDictSerializer):
    pk = serpy.IntField()
    prerendered = serpy.MethodField()
    primary_study = serpy.BoolField()
    pages = serpy.StrField(required=False)
    notes = serpy.StrField(required=False)

    def get_prerendered(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj["citation_json"])
        # strip out any newlines from the templating process
        citation = re.sub(r"\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class SourceComposerInventoryCompositionSerializer(ContextDictSerializer):
    folio_start = serpy.StrField(required=False)
    folio_end = serpy.StrField(required=False)
    uncertain = serpy.BoolField(required=False)
    source_attribution = serpy.StrField(attr="attribution", required=False)

    composition = serpy.StrField(attr="title", required=False)
    url = serpy.MethodField()

    def get_url(self, obj) -> str | None:
        if "id" not in obj or obj["id"] is None:
            return None

        return reverse(
            "composition-detail",
            kwargs={"pk": obj["id"]},
            request=self.context["request"],
        )


class SourceComposerInventorySerializer(ContextDictSerializer):
    url = serpy.MethodField(required=False)
    name = serpy.StrField(attr="composer_s")
    inventory = serpy.MethodField(required=False)

    def get_inventory(self, obj):
        inventory = SourceComposerInventoryCompositionSerializer(
            obj["compositions_json"],
            many=True,
            context={"request": self.context["request"]},
        ).data

        return [f for f in inventory if f]

    def get_url(self, obj) -> str | None:
        if "composer_i" not in obj or obj["composer_i"] is None:
            return None

        return reverse(
            "person-detail",
            kwargs={"pk": obj["composer_i"]},
            request=self.context["request"],
        )


class SourceInventoryNoteSerializer(serpy.Serializer):
    note = serpy.StrField(attr="note", required=False)
    note_type = serpy.StrField(attr="note_type", required=False)


class SourceInventoryBibliographySerializer(ContextDictSerializer):
    pk = serpy.IntField()
    prerendered = serpy.MethodField()
    pages = serpy.StrField(required=False)
    notes = serpy.StrField(required=False)

    def get_prerendered(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj["citation_json"])
        # strip out any newlines from the templating process
        citation = re.sub(r"\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class SourceUninventoriedSerializer(ContextSerializer):
    pk = serpy.IntField()
    composers = serpy.MethodField()

    def get_composers(self, obj) -> list | None:
        if obj.unattributed_composers.exists():
            out = []
            for comp in obj.unattributed_composers.all():
                out.append(
                    {
                        "full_name": str(comp.composer),
                        "url": reverse(
                            "person-detail",
                            kwargs={"pk": comp.composer.pk},
                            request=self.context["request"],
                        ),
                        "uncertain": comp.uncertain,
                        "note": comp.note,
                    }
                )
            return out


class SourceInventorySerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    num_voices = serpy.StrField(required=False)
    genres = serpy.MethodField(required=False)
    folio_start = serpy.StrField(required=False)
    folio_end = serpy.StrField(required=False)
    composition = serpy.StrField(required=False)
    composers = serpy.MethodField()
    item_title = serpy.StrField(required=False)
    bibliography = serpy.MethodField(required=False)
    voices = serpy.MethodField()
    pages = serpy.MethodField(required=False)
    source_attribution = serpy.StrField(required=False)
    notes = serpy.MethodField()

    def get_pages(self, obj):
        return [p.pk for p in obj.pages.all()]

    def get_genres(self, obj):
        if not obj.composition:
            return None
        return [g.name for g in obj.composition.genres.all()]

    def get_notes(self, obj):
        if not obj.notes:
            return None
        return SourceInventoryNoteSerializer(obj.notes.all(), many=True).data

    def get_bibliography(self, obj):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = ["type:bibliography", f"items_ii:{obj.pk}"]
        sort = "year_ans desc, sort_ans asc"

        connection.search("*:*", fq=fq, sort=sort)
        reslist = []
        for res in connection.results:
            if "items_json" in res:
                entry_list = [
                    s for s in res["items_json"] if s and s["item_id"] == obj.pk
                ]
                if not entry_list:
                    continue
                entry = entry_list[0]
                if p := entry.get("pages"):
                    res["pages"] = p
                if n := entry.get("notes"):
                    res["notes"] = n

                reslist.append(SourceInventoryBibliographySerializer(res).data)

        return reslist

    def get_url(self, obj):
        if not obj.composition:
            return None

        return reverse(
            "composition-detail",
            kwargs={"pk": obj.composition_id},
            request=self.context["request"],
        )

    def get_composers(self, obj) -> list | None:
        if not obj.composition:
            return None

        composers = obj.composition.composers.all()
        out = []
        for composer in composers:
            out.append(
                {
                    "full_name": str(composer.composer),
                    "url": reverse(
                        "person-detail",
                        kwargs={"pk": composer.composer.pk},
                        request=self.context["request"],
                    ),
                    "uncertain": composer.uncertain,
                }
            )

        return out or None

    def get_voices(self, obj) -> list | None:
        out = []
        for voice in obj.voices.all():
            d = {
                "voice_type": voice.type.name,
                "languages": [lang.name for lang in voice.languages.all()],
                "clef": str(voice.clef) if voice.clef else None,
                "voice_text": voice.voice_text,
                "mensuration": str(voice.mensuration) if voice.mensuration else None,
            }
            out.append({k: v for k, v in d.items() if v})

        return out or None


class SourceArchiveSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    siglum = serpy.StrField()
    city = serpy.StrField(attr="city.name")
    country = serpy.StrField(attr="city.parent.name", required=False)
    logo = serpy.MethodField()
    copyright = serpy.StrField(attr="copyright_statement", required=False)

    def get_url(self, obj):
        return reverse(
            "archive-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url


class SourceNoteSerializer(ContextSerializer):
    note = serpy.StrField()
    author = serpy.StrField()
    type = serpy.IntField()
    pk = serpy.IntField()
    note_type = serpy.StrField()


class SourceURLSerializer(ContextSerializer):
    type = serpy.IntField()
    url_type = serpy.StrField(attr="url_type")
    link = serpy.StrField()
    link_text = serpy.StrField()


class SourceNotationsSerializer(ContextSerializer):
    name = serpy.StrField()


class SourceIdentifierSerializer(ContextSerializer):
    identifier = serpy.StrField()
    type = serpy.IntField()
    identifier_type = serpy.StrField()
    note = serpy.StrField(required=False)


class SourceAuthoritiesSerializer(ContextSerializer):
    url = serpy.StrField(attr="identifier_url")
    label = serpy.StrField(attr="identifier_label")
    identifier = serpy.StrField()


class SourceListSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    display_name = serpy.StrField()
    shelfmark = serpy.StrField()

    def get_url(self, obj):
        return reverse(
            "source-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )


class SourceContributionSerializer(ContextSerializer):
    pk = serpy.IntField()
    summary = serpy.StrField()
    contributor = serpy.StrField(attr="contributor.full_name", required=False)
    credit = serpy.StrField(required=False)
    updated = DateTimeField(date_format="%A, %-d %B, %Y")


class SourceCommentarySerializer(ContextSerializer):
    pk = serpy.IntField()
    comment = serpy.StrField()
    author = serpy.StrField(attr="author.full_name", required=False)
    updated = DateTimeField(date_format="%A, %-d %B, %Y")


class SourceDetailSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    name = serpy.StrField(required=False)
    display_name = serpy.StrField(required=False)
    shelfmark = serpy.StrField()
    surface_type = serpy.StrField(required=False)
    date_statement = serpy.StrField(required=False)
    source_type = serpy.StrField(attr="type", required=False)
    format = serpy.StrField(required=False)
    measurements = serpy.StrField(required=False)
    type = serpy.MethodField()
    cover_image_info = serpy.MethodField(required=False)
    manifest_url = serpy.MethodField(required=False)
    inventory_provided = serpy.BoolField()
    public_images = serpy.BoolField()
    open_images = serpy.BoolField()
    has_external_images = serpy.MethodField()
    numbering_system_type = serpy.StrField(attr="numbering_system_type")

    has_images = serpy.MethodField(required=False)
    inventory = serpy.MethodField(required=False)
    composer_inventory = serpy.MethodField(required=False)
    uninventoried = serpy.MethodField(required=False)
    archive = serpy.MethodField(required=False)
    sets = serpy.MethodField(required=False)
    provenance = serpy.MethodField(required=False)
    relationships = serpy.MethodField(required=False)
    copyists = serpy.MethodField(required=False)
    catalogue_entries = serpy.MethodField(required=False)
    # iiif_manifest = serpy.MethodField()

    links = SourceURLSerializer(attr="links.all", call=True, many=True)

    bibliography = serpy.MethodField(required=False)
    identifiers = SourceIdentifierSerializer(
        attr="identifiers.all", call=True, many=True
    )
    notations = SourceNotationsSerializer(attr="notations.all", call=True, many=True)
    authorities = SourceAuthoritiesSerializer(
        attr="authorities.all", call=True, many=True
    )
    notes = serpy.MethodField(required=False)
    contributions = serpy.MethodField()
    commentary = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_url(self, obj):
        return reverse(
            "source-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_bibliography(self, obj) -> list[dict]:
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = ["type:bibliography", f"sources_ii:{obj.pk}"]
        connection.search("*:*", fq=fq, sort="year_ans desc, sort_ans asc")

        if connection.hits == 0:
            return []

        reslist = []
        for res in connection.results:
            if "sources_json" in res:
                entry_list = [
                    s for s in res["sources_json"] if s and s["source_id"] == obj.pk
                ]
                if not entry_list:
                    continue
                entry = entry_list[0]
                res["primary_study"] = entry["primary_study"]
                if p := entry.get("pages"):
                    res["pages"] = p
                if n := entry.get("notes"):
                    res["notes"] = n

                reslist.append(SourceBibliographySerializer(res).data)

        return reslist

    def get_notes(self, obj):
        # exclude private notes
        return SourceNoteSerializer(
            obj.notes.exclude(type=99).order_by("type", "sort"),
            many=True,
            context={"request": self.context["request"]},
        ).data

    def get_cover_image_info(self, obj):
        try:
            cover_obj = obj.cover
        except AttributeError:
            return None

        if not cover_obj:
            return None

        obj = {
            "url": reverse(
                "cover-image",
                kwargs={"pk": cover_obj["id"]},
                request=self.context["request"],
            ),
            "label": cover_obj["label"],
        }
        return obj

    def get_has_images(self, obj):
        return obj.pages.exists()

    def get_has_external_images(self, obj):
        return obj.links.filter(type=4).exists()

    def get_manifest_url(self, obj):
        # Return None if the document has no public images
        if not self.context["request"].user.is_authenticated:
            return None

        if not self.get_has_images(obj):
            return None

        return reverse(
            "source-manifest", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_inventory(self, obj):
        # source_order_f asc, folio_start_ans asc
        return SourceInventorySerializer(
            obj.inventory.select_related("composition", "source__archive__city")
            .prefetch_related(
                "composition__composers__composer",
                "composition__genres",
                "notes",
                "voices__languages",
                "voices__clef",
                "voices__type",
                "voices__mensuration",
                "pages",
                "unattributed_composers",
            )
            .filter(unattributed_composers__isnull=True)
            .order_by("source_order", Collate("folio_start", "natsort")),
            many=True,
            context={"request": self.context["request"]},
        ).data

    def get_composer_inventory(self, obj):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq: list = ["type:composerinventory", f"source_i:{obj.pk}"]
        sort: str = "composer_s asc"

        connection.search("*:*", fq=fq, sort=sort)

        composer_inventory = SourceComposerInventorySerializer(
            connection.results,
            many=True,
            context={"request": self.context["request"]},
        ).data

        return [c for c in composer_inventory if c.get("inventory")]

    def get_uninventoried(self, obj):
        return SourceUninventoriedSerializer(
            obj.inventory.filter(unattributed_composers__isnull=False)
            .distinct("pk")
            .order_by("pk"),
            many=True,
            context={"request": self.context["request"]},
        ).data

    def get_archive(self, obj):
        return SourceArchiveSerializer(
            obj.archive, context={"request": self.context["request"]}
        ).data

    def get_sets(self, obj):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq: list = ["type:set", f"sources_ii:{obj.pk}"]

        connection.search("*:*", fq=fq)

        return SourceSetSerializer(
            connection.results,
            many=True,
            context={"request": self.context["request"], "source_id": obj.pk},
        ).data

    def get_provenance(self, obj):
        return SourceProvenanceSerializer(
            obj.provenance.select_related(
                "city", "country", "region", "protectorate"
            ).all(),
            many=True,
            context={"request": self.context["request"]},
        ).data

    def get_relationships(self, obj):
        return SourceRelationshipSerializer(
            obj.relationships.select_related("relationship_type")
            .prefetch_related(
                GenericPrefetch(
                    "related_entity", [Person.objects.all(), Organization.objects.all()]
                )
            )
            .all(),
            many=True,
            context={"request": self.context["request"]},
        ).data

    def get_copyists(self, obj):
        return SourceCopyistSerializer(
            obj.copyists.all(), many=True, context={"request": self.context["request"]}
        ).data

    def get_catalogue_entries(self, obj):
        if not obj.catalogue_entries.count() > 0:
            return []

        return SourceCatalogueEntrySerializer(
            obj.catalogue_entries.all(),
            context={"request": self.context["request"]},
            many=True,
        ).data

    def get_contributions(self, obj):
        if not obj.contributions.count() > 0:
            return None

        return SourceContributionSerializer(
            obj.contributions.filter(accepted=True).order_by("-updated"),
            context={"request": self.context["request"]},
            many=True,
        ).data

    def get_commentary(self, obj):
        if not obj.commentary.count() > 0:
            return None

        public_comments = obj.commentary.filter(comment_type=1).exists()

        private_comments = None
        req = self.context["request"]
        if req.user.is_authenticated:
            private_comments = obj.commentary.filter(
                comment_type=0, author=req.user
            ).order_by("-updated")

        if not public_comments and not private_comments:
            return None

        all_comments = {
            "public": SourceCommentarySerializer(
                obj.commentary.filter(comment_type=1).order_by("-updated"),
                context={"request": self.context["request"]},
                many=True,
            ).data,
        }

        if private_comments:
            all_comments["private"] = SourceCommentarySerializer(
                private_comments,
                context={"request": self.context["request"]},
                many=True,
            ).data

        return all_comments
