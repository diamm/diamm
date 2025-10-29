import ypres
from rest_framework.reverse import reverse

from diamm.serializers.iiif.image import ImageSerializer


class CanvasSerializer(ypres.DictSerializer):
    id = ypres.MethodField(label="@id")
    type = ypres.StaticField(value="sc:Canvas", label="@type")
    label_ = ypres.StrField(label="label", attr="numeration_s")
    images = ypres.MethodField()
    width = ypres.IntField(attr="width_i")
    height = ypres.IntField(attr="height_i")

    def get_id(self, obj: dict) -> str:
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": obj["source_i"], "page_id": obj["pk"]},
            request=self.context["request"],
        )

    def get_images(self, obj: dict) -> list:
        context = {
            "source_id": obj["source_i"],
            "page_id": obj["pk"],
            "request": self.context["request"],
        }

        # the 'images' key is always an array.
        imgs_data = [ImageSerializer(obj, context=context).serialized]
        return imgs_data
