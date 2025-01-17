import serpy
from rest_framework.reverse import reverse

from diamm.serializers.fields import StaticField
from diamm.serializers.serializers import ContextDictSerializer


class ImageResourceSerializer(ContextDictSerializer):
    id = serpy.MethodField(label="@id")
    type = StaticField(label="@type", value="dctypes:Image")
    format = StaticField(value="image/jpeg")
    width = serpy.IntField(attr="width_i")
    height = serpy.IntField(attr="height_i")
    label = serpy.StrField(attr="image_type_s")
    service = serpy.MethodField()

    def get_id(self, obj: dict) -> str:
        return reverse(
            "image-serve-info",
            kwargs={"pk": obj["pk"]},
            request=self.context["request"],
        )

    def get_service(self, obj: dict) -> dict:
        proxied_image_url = reverse(
            "image-serve-info",
            kwargs={"pk": obj["pk"]},
            request=self.context["request"],
        )
        return {
            "@context": "http://iiif.io/api/image/2/context.json",
            "profile": "http://iiif.io/api/image/2/level1.json",
            "@id": proxied_image_url,
        }


class ImageSerializer(ContextDictSerializer):
    type = StaticField(label="@type", value="oa:Annotation")
    motivation = StaticField(value="sc:painting")
    on = serpy.MethodField()
    resource = serpy.MethodField()

    def get_on(self, obj: dict) -> str:
        page_id = self.context["page_id"]
        source_id = self.context["source_id"]
        request = self.context["request"]
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": source_id, "page_id": page_id},
            request=request,
        )

    def get_resource(self, obj: dict) -> dict:
        doclen = len(obj["_childDocuments_"])

        if doclen == 0:
            return {}

        if doclen == 1:
            return ImageResourceSerializer(
                obj["_childDocuments_"][0], context={"request": self.context["request"]}
            ).data
        else:
            imgs = obj["_childDocuments_"]

            return {
                "@type": "oa:Choice",
                "default": ImageResourceSerializer(
                    imgs[0], context={"request": self.context["request"]}
                ).data,
                "item": ImageResourceSerializer(
                    imgs[1:], many=True, context={"request": self.context["request"]}
                ).data,
            }
