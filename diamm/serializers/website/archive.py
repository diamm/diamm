import serpy
from rest_framework.reverse import reverse

from diamm.serializers.serializers import ContextSerializer


class SourceArchiveSerializer(ContextSerializer):
    url = serpy.MethodField()
    display_name = serpy.StrField(attr="display_name")
    # has_images = serpy.MethodField()

    public_images = serpy.BoolField(attr="public_images")
    # cover_image = serpy.MethodField(required=False)
    #
    source_type = serpy.StrField(attr="type", required=False)
    date_statement = serpy.StrField(attr="date_statement", required=False)
    # surface = serpy.StrField(attr="surface_type_s", required=False)

    def get_url(self, obj):
        return reverse(
            "source-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_cover_image(self, obj):
        if not obj.get("cover_image_i"):
            return None

        return reverse(
            "image-serve",
            kwargs={
                "pk": obj["cover_image_i"],
                "region": "full",
                "size": "100,",
                "rotation": 0,
            },
            request=self.context["request"],
        )


class ArchiveIdentifierSerializer(ContextSerializer):
    url = serpy.StrField(attr="identifier_url")
    label = serpy.StrField(attr="identifier_label")
    identifier = serpy.StrField()


class CityArchiveSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    country = serpy.StrField(attr="parent.name")

    def get_url(self, obj):
        return reverse(
            "city-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )


class ArchiveNoteSerializer(ContextSerializer):
    note = serpy.StrField()
    note_type = serpy.StrField()
    type_ = serpy.IntField(attr="type")


class ArchiveDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    pk = serpy.IntField()
    sources = serpy.MethodField()
    city = serpy.MethodField()
    former_name = serpy.StrField(required=False)
    name = serpy.StrField()
    siglum = serpy.StrField()
    website = serpy.StrField(required=False)
    logo = serpy.MethodField()
    notes = serpy.MethodField()
    identifiers = serpy.MethodField(required=False)

    def get_url(self, obj):
        return reverse(
            "archive-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_city(self, obj):
        return CityArchiveSerializer(
            obj.city, context={"request": self.context["request"]}
        ).data

    def get_sources(self, obj):
        return SourceArchiveSerializer(
            obj.sources.all(), many=True, context={"request": self.context["request"]}
        ).data

    def get_notes(self, obj) -> list:
        return ArchiveNoteSerializer(obj.notes.exclude(type=1), many=True).data

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url

    def get_identifiers(self, obj) -> list:
        return ArchiveIdentifierSerializer(
            obj.identifiers.all(),
            many=True,
            context={"request": self.context["request"]},
        ).data
