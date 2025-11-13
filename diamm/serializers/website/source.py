import re
from functools import cached_property

import ypres
from django.conf import settings
from django.contrib.contenttypes.prefetch import GenericPrefetch
from django.db.models import Count, Prefetch
from django.db.models.functions import Collate
from django.template.loader import get_template
from rest_framework.reverse import reverse

from diamm.helpers.formatters import contents_statement
from diamm.helpers.solr_helpers import SolrManager
from diamm.models import (
    CompositionComposer,
    ItemNote,
    Organization,
    Person,
    SourceURL,
    Voice,
)
from diamm.models.data.item import CompletenessOptionsChoices
from diamm.models.data.item_note import ItemNoteTypeChoices

# from diamm.serializers.fields import DateTimeField
# from diamm.serializers.serializers import ContextDictSerializer, ypres.Serializer


class SourceCatalogueEntrySerializer(ypres.Serializer):
    entry = ypres.MethodField()
    order = ypres.IntField()

    def get_entry(self, obj) -> str:
        request = self.context["request"]
        return (
            f"{request.scheme}://{request.get_host()}/media/rism/catalogue/{obj.entry}"
        )


class SourceCopyistSerializer(ypres.Serializer):
    copyist = ypres.MethodField()
    uncertain = ypres.BoolField(attr="uncertain", required=False)
    type = ypres.StrField(attr="get_type_display", call=True)
    type_s = ypres.StrField(attr="get_type_display", call=True)

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


class SourceRelationshipSerializer(ypres.Serializer):
    related_entity = ypres.MethodField()
    uncertain = ypres.BoolField(attr="uncertain", required=False)
    relationship_type = ypres.StrField(attr="relationship_type")

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


class SourceProvenanceSerializer(ypres.Serializer):
    city = ypres.StrField(attr="city.name", required=False)
    country = ypres.StrField(attr="country.name", required=False)
    region = ypres.StrField(attr="region.name", required=False)
    protectorate = ypres.StrField(attr="protectorate.name", required=False)
    entity = ypres.MethodField()
    country_uncertain = ypres.BoolField(attr="country_uncertain")
    city_uncertain = ypres.BoolField(attr="city_uncertain")
    entity_uncertain = ypres.BoolField(attr="entity_uncertain")
    region_uncertain = ypres.BoolField(attr="region_uncertain")

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


class SourceSetSerializer(ypres.DictSerializer):
    pk = ypres.IntField()
    url = ypres.MethodField()
    cluster_shelfmark = ypres.StrField(attr="cluster_shelfmark_s")
    set_type = ypres.StrField(attr="set_type_s")
    sources = ypres.MethodField()

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


class SourceBibliographySerializer(ypres.DictSerializer):
    pk = ypres.IntField()
    prerendered = ypres.MethodField()
    primary_study = ypres.BoolField()
    pages = ypres.StrField(required=False)
    notes = ypres.StrField(required=False)

    def get_prerendered(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj["citation_json"])
        # strip out any newlines from the templating process
        citation = re.sub(r"\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class SourceComposerInventoryCompositionSerializer(ypres.DictSerializer):
    folio_start = ypres.StrField(required=False)
    folio_end = ypres.StrField(required=False)
    uncertain = ypres.BoolField(required=False)
    source_attribution = ypres.StrField(attr="attribution", required=False)

    composition = ypres.StrField(attr="title", required=False)
    fragment = ypres.BoolField(required=False)
    completeness = ypres.MethodField()
    url = ypres.MethodField()

    def get_url(self, obj) -> str | None:
        if "id" not in obj or obj["id"] is None:
            return None

        return reverse(
            "composition-detail",
            kwargs={"pk": obj["id"]},
            request=self.context["request"],
        )

    def get_completeness(self, obj) -> str | None:
        if "completeness" not in obj:
            return None
        d = dict(CompletenessOptionsChoices.choices)
        return d[obj["completeness"]]


class SourceComposerInventorySerializer(ypres.DictSerializer):
    url = ypres.MethodField(required=False)
    name = ypres.StrField(attr="composer_s")
    inventory = ypres.MethodField(required=False)

    def get_inventory(self, obj):
        inventory = SourceComposerInventoryCompositionSerializer(
            obj["compositions_json"],
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many

        return [f for f in inventory if f]

    def get_url(self, obj) -> str | None:
        if "composer_i" not in obj or obj["composer_i"] is None:
            return None

        return reverse(
            "person-detail",
            kwargs={"pk": obj["composer_i"]},
            request=self.context["request"],
        )


class SourceInventoryNoteSerializer(ypres.Serializer):
    note = ypres.StrField(attr="note", required=False)
    note_type = ypres.StrField(attr="note_type", required=False)


class SourceInventoryBibliographySerializer(ypres.DictSerializer):
    # pk = ypres.IntField(required=False)
    prerendered = ypres.MethodField()
    pages = ypres.StrField(required=False, attr="citation_pages")
    notes = ypres.StrField(required=False, attr="citation_notes")

    def get_prerendered(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj)
        # strip out any newlines from the templating process
        citation = re.sub(r"\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class SourceUninventoriedSerializer(ypres.Serializer):
    pk = ypres.IntField()
    composers = ypres.MethodField()

    def get_composers(self, obj) -> list | None:
        if not obj.unattributed_composers.exists():
            return None

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


class SourceInventorySerializer(ypres.Serializer):
    pk = ypres.IntField()
    url = ypres.MethodField()
    num_voices = ypres.StrField(required=False)
    genres = ypres.MethodField(required=False)
    folio_start = ypres.StrField(required=False)
    folio_end = ypres.StrField(required=False)
    composition = ypres.StrField(required=False)
    composers = ypres.MethodField()
    item_title = ypres.StrField(required=False)
    bibliography = ypres.MethodField()
    voices = ypres.MethodField()
    pages = ypres.MethodField()
    source_attribution = ypres.StrField(required=False)
    notes = ypres.MethodField()
    fragment = ypres.BoolField()
    completeness = ypres.StrField(attr="item_completeness")

    def get_pages(self, obj):
        return [p.pk for p in obj.pages.all()]

    def get_genres(self, obj):
        if not obj.composition:
            return None
        return [g.name for g in obj.composition.genres.all()]

    def get_notes(self, obj):
        if not obj.notes:
            return None
        return SourceInventoryNoteSerializer(obj.notes, many=True).serialized_many

    def get_bibliography(self, obj) -> list | None:
        bibl = obj.bibliography_json
        if not bibl:
            return None
        return SourceInventoryBibliographySerializer(bibl, many=True).serialized_many

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


class SourceArchiveSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()
    siglum = ypres.StrField()
    city = ypres.StrField(attr="city.name")
    country = ypres.StrField(attr="city.parent.name", required=False)
    logo = ypres.MethodField()
    copyright = ypres.StrField(attr="copyright_statement", required=False)

    def get_url(self, obj):
        return reverse(
            "archive-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url


class SourceNoteSerializer(ypres.Serializer):
    note = ypres.StrField()
    author = ypres.StrField()
    type = ypres.IntField()
    pk = ypres.IntField()
    note_type = ypres.StrField()


class SourceURLSerializer(ypres.Serializer):
    type = ypres.IntField()
    url_type = ypres.StrField(attr="url_type")
    link = ypres.StrField()
    link_text = ypres.StrField()


class SourceNotationsSerializer(ypres.Serializer):
    name = ypres.StrField()


class SourceIdentifierSerializer(ypres.Serializer):
    identifier = ypres.StrField()
    type = ypres.IntField()
    identifier_type = ypres.StrField()
    note = ypres.StrField(required=False)


class SourceAuthoritiesSerializer(ypres.Serializer):
    url = ypres.StrField(attr="identifier_url")
    alabel = ypres.StrField(label="label", attr="identifier_label")
    identifier = ypres.StrField()


class SourceListSerializer(ypres.Serializer):
    pk = ypres.IntField()
    url = ypres.MethodField()
    display_name = ypres.StrField()
    shelfmark = ypres.StrField()

    def get_url(self, obj):
        return reverse(
            "source-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )


class SourceContributionSerializer(ypres.Serializer):
    pk = ypres.IntField()
    summary = ypres.StrField()
    contributor = ypres.StrField(attr="contributor.full_name", required=False)
    credit = ypres.StrField(required=False)
    updated = ypres.DateTimeField(date_format="%A, %-d %B, %Y")


class SourceCommentarySerializer(ypres.Serializer):
    pk = ypres.IntField()
    comment = ypres.StrField()
    author = ypres.StrField(attr="author.full_name", required=False)
    updated = ypres.DateTimeField(date_format="%A, %-d %B, %Y")


class SourceDetailSerializer(ypres.Serializer):
    pk = ypres.IntField()
    url = ypres.MethodField()
    name = ypres.StrField(required=False)
    display_name = ypres.StrField(required=False)
    shelfmark = ypres.StrField()
    surface_type = ypres.StrField(required=False)
    date_statement = ypres.StrField(required=False)
    source_type = ypres.StrField(attr="type", required=False)
    format = ypres.StrField(required=False)
    measurements = ypres.StrField(required=False)
    type = ypres.MethodField()
    cover_image_info = ypres.MethodField(required=False)
    manifest_url = ypres.MethodField(required=False)
    inventory_provided = ypres.BoolField()
    public_images = ypres.BoolField()
    open_images = ypres.BoolField()
    has_external_images = ypres.MethodField()
    has_external_manifest = ypres.MethodField()
    numbering_system_type = ypres.StrField(attr="numbering_system_type")

    has_images = ypres.MethodField(required=False)
    inventory = ypres.MethodField(required=False)
    composer_inventory = ypres.MethodField(required=False)
    uninventoried = ypres.MethodField(required=False)
    archive = ypres.MethodField(required=False)
    sets = ypres.MethodField(required=False)
    provenance = ypres.MethodField(required=False)
    relationships = ypres.MethodField(required=False)
    copyists = ypres.MethodField(required=False)
    catalogue_entries = ypres.MethodField(required=False)
    contents_statement = ypres.MethodField()
    # iiif_manifest = ypres.MethodField()

    links = SourceURLSerializer(attr="links.all", call=True, many=True)

    bibliography = ypres.MethodField(required=False)
    identifiers = SourceIdentifierSerializer(
        attr="identifiers.all", call=True, many=True
    )
    notations = SourceNotationsSerializer(attr="notations.all", call=True, many=True)
    authorities = SourceAuthoritiesSerializer(
        attr="authorities.all", call=True, many=True
    )
    notes = ypres.MethodField(required=False)
    contributions = ypres.MethodField()
    commentary = ypres.MethodField()

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

                reslist.append(SourceBibliographySerializer(res).serialized)

        return reslist

    def get_notes(self, obj):
        # exclude private notes
        return SourceNoteSerializer(
            obj.notes.exclude(type=99).order_by("type", "sort"),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many

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

    def get_has_images(self, obj) -> bool:
        return obj.images_are_public

    def get_has_external_images(self, obj):
        return obj.links.filter(type=4).exists()

    def get_has_external_manifest(self, obj) -> bool:
        return obj.images_are_public is False and obj.has_manifest_link is True

    def get_manifest_url(self, obj):
        # The assumption here is that if we have an external manifest,
        # it is public.
        # Return None if the document has no public images
        if not obj.images_are_public:
            if iiif_link := obj.links.filter(type=SourceURL.IIIF_MANIFEST).first():
                return iiif_link.link
            return None

        return reverse(
            "source-manifest", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_inventory(self, obj):
        # source_order_f asc, folio_start_ans asc
        # Pull Voice subtree in one go
        voices_qs = (
            Voice.objects.select_related(
                "type", "clef", "mensuration"
            )  # FKs: 0 extra queries
            .prefetch_related(
                "languages"
            )  # M2M: 1 query for all languages across all voices
            .order_by("sort_order", "id")  # stable order per item
        )

        notes_qs = (
            ItemNote.objects.only("id", "item_id", "type", "note")
            .order_by("type", "id")
            .exclude(note_type=ItemNoteTypeChoices.INTERNAL)
        )

        return SourceInventorySerializer(
            obj.inventory.select_related(
                "composition",
                "source",
                "source__archive",
                "source__archive__city",
            )
            .prefetch_related(
                # Composition composers in two hops, but as two queries total:
                Prefetch(
                    "composition__composers",
                    queryset=(
                        CompositionComposer.objects.select_related(
                            "composer"
                        )  # pulls the Person in same query
                    ),
                ),
                Prefetch("notes", queryset=notes_qs),
                "composition__genres",  # single query
                Prefetch(
                    "voices", queryset=voices_qs
                ),  # replaces all voices__* prefetches
                "pages",  # single query
                "unattributed_composers",  # single query (for display)
                # If notes is heavy, constrain it:
                # Prefetch('notes', queryset=Note.objects.select_related('created_by').only('id','item_id','text','created_by_id'))
            )
            # Safer “no unattributed composers” filter that won’t be confused by other M2M joins:
            .annotate(_ua_count=Count("unattributed_composers", distinct=True))
            .filter(_ua_count=0)
            # If you stick with .filter(unattributed_composers__isnull=True), add .distinct() below.
            .order_by("source_order", Collate("folio_start", "natsort")),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many

    def get_composer_inventory(self, obj):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq: list = ["type:composerinventory", f"source_i:{obj.pk}"]
        sort: str = "composer_s asc"

        connection.search("*:*", fq=fq, sort=sort)

        composer_inventory = SourceComposerInventorySerializer(
            connection.results,
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many

        return [c for c in composer_inventory if c.get("inventory")]

    def get_uninventoried(self, obj):
        return SourceUninventoriedSerializer(
            obj.inventory.filter(unattributed_composers__isnull=False)
            .distinct("pk")
            .order_by("pk"),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many

    def get_archive(self, obj):
        return SourceArchiveSerializer(
            obj.archive, context={"request": self.context["request"]}
        ).serialized

    def get_sets(self, obj):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq: list = ["type:set", f"sources_ii:{obj.pk}"]

        connection.search("*:*", fq=fq)

        return SourceSetSerializer(
            connection.results,
            many=True,
            context={"request": self.context["request"], "source_id": obj.pk},
        ).serialized_many

    def get_provenance(self, obj):
        return SourceProvenanceSerializer(
            obj.provenance.select_related(
                "city", "country", "region", "protectorate"
            ).all(),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many

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
        ).serialized_many

    def get_copyists(self, obj):
        return SourceCopyistSerializer(
            obj.copyists.all(), many=True, context={"request": self.context["request"]}
        ).serialized_many

    def get_catalogue_entries(self, obj):
        if not obj.catalogue_entries.count() > 0:
            return []

        return SourceCatalogueEntrySerializer(
            obj.catalogue_entries.all(),
            context={"request": self.context["request"]},
            many=True,
        ).serialized_many

    def get_contributions(self, obj):
        if not obj.contributions.exists():
            return None

        return SourceContributionSerializer(
            obj.contributions.select_related("contributor")
            .filter(accepted=True)
            .order_by("-updated"),
            context={"request": self.context["request"]},
            many=True,
        ).serialized_many

    def get_commentary(self, obj):
        if not obj.commentary.exists():
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
                obj.commentary.select_related("author")
                .filter(comment_type=1)
                .order_by("-updated"),
                context={"request": self.context["request"]},
                many=True,
            ).serialized_many,
        }

        if private_comments:
            all_comments["private"] = SourceCommentarySerializer(
                private_comments,
                context={"request": self.context["request"]},
                many=True,
            ).serialized_many

        return all_comments

    def get_contents_statement(self, obj) -> str | None:
        connection = SolrManager(settings.SOLR["SERVER"])
        fq: list = ["type:source", f"pk:{obj.pk}"]

        connection.search(
            "*:*",
            fq=fq,
            fl=[
                "pk",
                "number_of_anonymous_compositions_i",
                "number_of_attributed_compositions_i",
                "number_of_compositions_i",
                "number_of_composers_i",
                "number_of_uninventoried_composers_i",
            ],
        )

        if connection.hits == 0:
            return None
        doc: dict = connection.docs[0]

        return contents_statement(doc)
