import serpy
from rest_framework.reverse import reverse

from diamm.serializers.fields import StaticField
from diamm.serializers.iiif.image import ImageSerializer
from diamm.serializers.serializers import ContextDictSerializer


class CanvasSerializer(ContextDictSerializer):
    id = serpy.MethodField(label="@id")
    type = StaticField(value="sc:Canvas", label="@type")
    label = serpy.StrField(attr="numeration_s")
    images = serpy.MethodField()
    width = serpy.IntField(attr="width_i")
    height = serpy.IntField(attr="height_i")

    def get_id(self, obj: dict) -> str:
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": obj["source_i"], "page_id": obj["page_i"]},
            request=self.context["request"],
        )

    def get_images(self, obj: dict) -> list:
        context = {
            "source_id": obj["source_i"],
            "page_id": obj["pk"],
            "request": self.context["request"],
        }

        # the 'images' key is always an array.
        imgs_data = [ImageSerializer(obj, context=context).data]
        return imgs_data
