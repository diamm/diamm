from typing import Optional

import serpy
from rest_framework.reverse import reverse

from diamm.serializers.serializers import ContextSerializer


class SetSourceSerializer(ContextSerializer):
    url = serpy.MethodField()
    shelfmark = serpy.StrField()
    public_images = serpy.BoolField()
    has_images = serpy.MethodField()
    display_name = serpy.StrField(required=False)
    archive_name = serpy.StrField(attr="archive.display_name")
    cover = serpy.MethodField()

    def get_url(self, obj) -> str:
        return reverse(
            "source-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_has_images(self, obj) -> bool:
        return obj.pages.exists()

    def get_cover(self, obj) -> Optional[str]:
        try:
            cover_obj = obj.cover
        except AttributeError:
            return None

        if not cover_obj:
            return None

        return reverse(
            "image-serve-info",
            kwargs={"pk": cover_obj["id"]},
            request=self.context["request"],
        )


class SetDetailSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    type = serpy.StrField(attr="set_type")
    cluster_shelfmark = serpy.StrField()
    sources = serpy.MethodField()
    description = serpy.StrField(required=False)

    def get_url(self, obj) -> str:
        return reverse(
            "set-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_sources(self, obj) -> Optional[list]:
        return SetSourceSerializer(
            obj.sources.all().select_related("archive__city").prefetch_related("pages"),
            many=True,
            context={"request": self.context["request"]},
        ).data
