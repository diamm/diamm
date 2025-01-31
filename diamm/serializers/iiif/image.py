import serpy
from django.conf import settings
from rest_framework.reverse import reverse

from diamm.helpers.solr_helpers import SolrManager
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
        if alt_ids := obj.get("alt_images_ii"):
            conn = SolrManager(settings.SOLR["SERVER"])

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
            print(canvas_query)
            conn.search("*:*", **canvas_query)

            return {
                "@type": "oa:Choice",
                "default": ImageResourceSerializer(
                    obj, context={"request": self.context["request"]}
                ).data,
                "item": ImageResourceSerializer(
                    conn.results,
                    many=True,
                    context={"request": self.context["request"]},
                ).data,
            }

        return ImageResourceSerializer(
            obj, context={"request": self.context["request"]}
        ).data
        # else:
        #     imgs = obj["_childDocuments_"]
        #
        #     return {
        #         "@type": "oa:Choice",
        #         "default": ImageResourceSerializer(
        #             imgs[0], context={"request": self.context["request"]}
        #         ).data,
        #         "item": ImageResourceSerializer(
        #             imgs[1:], many=True, context={"request": self.context["request"]}
        #         ).data,
        #     }
