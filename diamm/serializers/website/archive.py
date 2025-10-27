import ypres
from django.db.models.expressions import Exists, OuterRef
from django.db.models.functions.comparison import Collate
from rest_framework.reverse import reverse

from diamm.models import Page, SourceURL


class SourceArchiveSerializer(ypres.Serializer):
    url = ypres.MethodField()
    display_name = ypres.StrField(attr="display_name")
    public_images = ypres.BoolField(attr="public_images")
    source_type = ypres.StrField(attr="type", required=False)
    date_statement = ypres.StrField(attr="date_statement", required=False)
    has_external_manifest = ypres.MethodField()

    def get_url(self, obj):
        return reverse(
            "source-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_has_external_manifest(self, obj) -> bool:
        return obj.images_are_public is False and obj.has_manifest_link is True


class ArchiveIdentifierSerializer(ypres.Serializer):
    url = ypres.StrField(attr="identifier_url")
    alabel = ypres.StrField(label="label", attr="identifier_label")
    identifier = ypres.StrField()


class CityArchiveSerializer(ypres.Serializer):
    url = ypres.MethodField()
    name = ypres.StrField()
    country = ypres.StrField(attr="parent.name")

    def get_url(self, obj):
        return reverse(
            "city-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )


class ArchiveNoteSerializer(ypres.Serializer):
    note = ypres.StrField()
    note_type = ypres.StrField()
    type_ = ypres.IntField(attr="type")


class ArchiveDetailSerializer(ypres.Serializer):
    url = ypres.MethodField()
    pk = ypres.IntField()
    sources = ypres.MethodField()
    city = ypres.MethodField()
    former_name = ypres.StrField(required=False)
    name = ypres.StrField()
    siglum = ypres.StrField()
    website = ypres.StrField(required=False)
    logo = ypres.MethodField()
    notes = ypres.MethodField()
    identifiers = ypres.MethodField(required=False)

    def get_url(self, obj):
        return reverse(
            "archive-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_city(self, obj):
        return CityArchiveSerializer(
            obj.city, context={"request": self.context["request"]}
        ).serialized

    def get_sources(self, obj):
        req = self.context["request"]
        public_filter = {} if req.user.is_staff else {"public": True}
        return SourceArchiveSerializer(
            obj.sources.filter(**public_filter)
            .order_by(Collate("shelfmark", collation="natsort"))
            .annotate(
                images_are_public=Exists(
                    Page.objects.filter(source=OuterRef("pk"), images__public=True)
                ),
                has_manifest_link=Exists(
                    SourceURL.objects.filter(
                        source=OuterRef("pk"), type=SourceURL.IIIF_MANIFEST
                    )
                ),
            ),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many

    def get_notes(self, obj) -> list:
        return ArchiveNoteSerializer(
            obj.notes.exclude(type=1), many=True
        ).serialized_many

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url

    def get_identifiers(self, obj) -> list:
        return ArchiveIdentifierSerializer(
            obj.identifiers.all(),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many
