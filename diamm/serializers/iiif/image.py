import ypres
from rest_framework.reverse import reverse

from diamm.helpers.solr import SolrManager


class ImageResourceSerializer(ypres.DictSerializer):
    id = ypres.MethodField()
    type = ypres.StaticField(value="Image")
    format = ypres.StaticField(value="image/jpeg")
    width = ypres.IntField(attr="width_i")
    height = ypres.IntField(attr="height_i")
    label = ypres.MethodField(required=False)
    service = ypres.MethodField()

    def get_id(self, obj: dict) -> str:
        service_id = reverse(
            "image-serve-redirect",
            kwargs={"pk": obj["pk"]},
            request=self.context["request"],
        )
        return f"{service_id}full/full/0/default.jpg"

    def get_label(self, obj: dict) -> dict | None:
        if "image_type_s" not in obj:
            return None

        return {"none": [obj["image_type_s"]]}

    def get_service(self, obj: dict) -> list[dict]:
        proxied_image_url = reverse(
            "image-serve-redirect",
            kwargs={"pk": obj["pk"]},
            request=self.context["request"],
        )
        return [
            {
                "id": proxied_image_url,
                "type": "ImageService2",
                "profile": "level1",
            }
        ]


class ImageSerializer(ypres.DictSerializer):
    id = ypres.MethodField()
    type = ypres.StaticField(value="Annotation")
    motivation = ypres.StaticField(value="painting")
    body = ypres.MethodField()
    target = ypres.MethodField()

    def _canvas_id(self) -> str:
        return self.context.get("canvas_id") or reverse(
            "source-canvas-detail",
            kwargs={
                "source_id": self.context["source_id"],
                "page_id": self.context["page_id"],
            },
            request=self.context["request"],
        )

    def get_id(self, obj: dict) -> str:
        del obj
        return f"{self._canvas_id()}/annotation/0"

    def get_target(self, obj: dict) -> str:
        del obj
        return self._canvas_id()

    def get_body(self, obj: dict) -> dict:
        if alt_ids := obj.get("alt_images_ii", []):
            conn = SolrManager()

            # image_type_i:1 in the field list transformer childFilter ensures that
            # only the primary images (type 1) are returned.
            # images_ss:[* TO *] ensures that only records with images attached are returned.
            canvas_query = {
                "fq": [
                    "type:image",
                    f"{{!terms f=pk}}{','.join(str(s) for s in alt_ids)}",
                    "!image_type_i:1",
                ],
                "sort": "sort_order_f asc, image_type_i asc, numeration_ans asc",
            }
            conn.search("*:*", **canvas_query)

            return {
                "type": "Choice",
                "items": [
                    ImageResourceSerializer(
                        obj, context={"request": self.context["request"]}
                    ).serialized,
                    *ImageResourceSerializer(
                        conn.results,
                        many=True,
                        context={"request": self.context["request"]},
                    ).serialized_many,
                ],
            }

        return ImageResourceSerializer(
            obj, context={"request": self.context["request"]}
        ).serialized
