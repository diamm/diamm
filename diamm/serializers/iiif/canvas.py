import ypres
from rest_framework.reverse import reverse

from diamm.serializers.iiif.helpers import language_map
from diamm.serializers.iiif.image import ImageSerializer


class CanvasSerializer(ypres.DictSerializer):
    id = ypres.MethodField()
    type = ypres.StaticField(value="Canvas")
    label = ypres.MethodField()
    items = ypres.MethodField()
    width = ypres.IntField(attr="width_i")
    height = ypres.IntField(attr="height_i")

    def get_id(self, obj: dict) -> str:
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": obj["source_i"], "page_id": obj["pk"]},
            request=self.context["request"],
        )

    def get_label(self, obj: dict) -> dict:
        return language_map(obj.get("numeration_s", f"Page {obj['pk']}"))

    def get_items(self, obj: dict) -> list:
        canvas_id = self.get_id(obj)
        context = {
            "source_id": obj["source_i"],
            "page_id": obj["pk"],
            "request": self.context["request"],
            "canvas_id": canvas_id,
        }

        return [
            {
                "id": f"{canvas_id}/annotation-page/0",
                "type": "AnnotationPage",
                "items": [ImageSerializer(obj, context=context).serialized],
            }
        ]
