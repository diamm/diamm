import ypres
from django.contrib.contenttypes.prefetch import GenericPrefetch
from django.db.models.expressions import Exists, OuterRef
from django.db.models.query import Prefetch
from rest_framework.reverse import reverse

from diamm.models import Item, Organization, Page, Person, SourceURL
from diamm.models.data.person_note import PersonNote


class PersonRoleSerializer(ypres.Serializer):
    earliest_year = ypres.StrField(required=False)
    earliest_year_approximate = ypres.BoolField()
    latest_year_approximate = ypres.BoolField()
    latest_year = ypres.StrField(required=False)
    role = ypres.StrField(attr="role_description")
    note = ypres.StrField(required=False)


class PersonNoteSerializer(ypres.Serializer):
    note = ypres.StrField()


class PersonContributionSerializer(ypres.Serializer):
    contributor = ypres.StrField(attr="contributor.username")
    summary = ypres.StrField()
    updated = ypres.StrField()


class PersonSourceCopyistSerializer(ypres.Serializer):
    url = ypres.MethodField()
    has_images = ypres.BoolField(attr="source.pages.exists", call=True, required=False)
    copyist_type = ypres.StrField(attr="copyist_type")
    uncertain = ypres.BoolField(attr="uncertain")
    source = ypres.StrField(attr="source.display_name")
    public_images = ypres.BoolField(attr="source.public_images", required=False)

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source_id},
            request=self.context["request"],
        )


class PersonSourceRelationshipSerializer(ypres.Serializer):
    url = ypres.MethodField()
    relationship = ypres.StrField(attr="relationship_type")
    uncertain = ypres.BoolField(attr="uncertain")
    source = ypres.StrField(attr="source.display_name")
    has_images = ypres.BoolField(attr="images_are_public", required=False)
    public_images = ypres.BoolField(attr="source.public_images", required=False)

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.source_id},
            request=self.context["request"],
        )

    def get_has_external_manifest(self, obj) -> bool:
        return obj.images_are_public is False and obj.has_manifest_link is True


class PersonCompositionSerializer(ypres.Serializer):
    url = ypres.MethodField()
    title = ypres.StrField(attr="composition.title")
    uncertain = ypres.BoolField()
    sources = ypres.MethodField()

    def get_url(self, obj) -> str:
        return reverse(
            "composition-detail",
            kwargs={"pk": obj.composition_id},
            request=self.context["request"],
        )

    def get_sources(self, obj):
        req = self.context["request"]
        items = obj.composition.sources.all()
        ret = []
        for item in items:
            if not req.user.is_staff and not item.source.public:
                continue

            url = reverse(
                "source-detail",
                kwargs={"pk": item.source.pk},
                request=self.context["request"],
            )
            name = item.source.display_name

            ret.append({"url": url, "name": name})
        return ret


class PersonIdentifierSerializer(ypres.Serializer):
    url = ypres.StrField(attr="identifier_url")
    alabel = ypres.StrField(label="label", attr="identifier_label")
    identifier = ypres.StrField()


class PersonUninventoriedItemsSerializer(ypres.Serializer):
    title = ypres.StrField("item.title", required=False)
    source = ypres.StrField("item.source.display_name")
    source_url = ypres.MethodField()

    def get_source_url(self, obj):
        return reverse(
            "source-detail",
            kwargs={"pk": obj.item.source_id},
            request=self.context["request"],
        )


class PersonDetailSerializer(ypres.Serializer):
    url = ypres.MethodField()
    pk = ypres.IntField()
    compositions = ypres.MethodField()
    related_sources = ypres.MethodField()
    copied_sources = ypres.MethodField()
    full_name = ypres.StrField()
    type = ypres.MethodField()
    earliest_year = ypres.IntField(required=False)
    earliest_year_approximate = ypres.BoolField(required=False)
    latest_year = ypres.IntField(required=False)
    latest_year_approximate = ypres.BoolField(required=False)
    # biography = ypres.MethodField()
    variant_names = ypres.MethodField()
    roles = ypres.MethodField()
    identifiers = ypres.MethodField(required=False)
    uninventoried_items = ypres.MethodField()

    def get_url(self, obj) -> str:
        return reverse(
            "person-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_uninventoried_items(self, obj):
        return PersonUninventoriedItemsSerializer(
            obj.unattributed_works.select_related("item__source__archive").distinct(
                "item__source"
            ),
            context={"request": self.context["request"]},
            many=True,
        ).serialized_many

    def get_compositions(self, obj) -> list:
        return PersonCompositionSerializer(
            obj.compositions.select_related("composition", "composer")
            .prefetch_related(
                Prefetch(
                    "composition__sources",
                    queryset=Item.objects.select_related("source__archive").order_by(
                        "source__archive__siglum", "source__shelfmark"
                    ),
                ),
                "composition__composers__composer",
            )
            .all(),
            context={"request": self.context["request"]},
            many=True,
        ).serialized_many

    def get_related_sources(self, obj) -> list:
        return PersonSourceRelationshipSerializer(
            obj.sources_related.select_related(
                "relationship_type", "source__archive__city"
            )
            .prefetch_related(
                GenericPrefetch(
                    "related_entity", [Person.objects.all(), Organization.objects.all()]
                ),
                "source__inventory",
            )
            .annotate(
                images_are_public=Exists(
                    Page.objects.filter(
                        source=OuterRef("source_id"), images__public=True
                    )
                ),
                has_manifest_link=Exists(
                    SourceURL.objects.filter(
                        source=OuterRef("source_id"), type=SourceURL.IIIF_MANIFEST
                    )
                ),
            )
            .order_by("source__archive__siglum", "source__shelfmark"),
            context={"request": self.context["request"]},
            many=True,
        ).serialized_many

    def get_copied_sources(self, obj) -> list:
        return PersonSourceCopyistSerializer(
            obj.sources_copied.select_related("source__archive__city")
            .prefetch_related(
                GenericPrefetch(
                    "copyist",
                    [
                        Person.objects.prefetch_related("identifiers", "roles").all(),
                        Organization.objects.prefetch_related("identifiers").all(),
                    ],
                ),
                "source__pages__images",
                "source__inventory",
            )
            .all(),
            context={"request": self.context["request"]},
            many=True,
        ).serialized_many

    def get_type(self, obj) -> str:
        return obj.__class__.__name__.lower()

    # def get_biography(self, obj):
    #     return PersonNoteSerializer(obj.notes.filter(type=PersonNote.BIOGRAPHY, public=True), many=True).data

    def get_variant_names(self, obj) -> list:
        return list(
            obj.notes.filter(
                type=PersonNote.VARIANT_NAME_NOTE, public=True
            ).values_list("note", flat=True)
        )

    def get_roles(self, obj) -> list:
        return PersonRoleSerializer(obj.roles.all(), many=True).serialized_many

    def get_identifiers(self, obj) -> list:
        return PersonIdentifierSerializer(
            obj.identifiers.all(),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many
