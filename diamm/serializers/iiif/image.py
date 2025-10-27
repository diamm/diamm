import ypres
from django.conf import settings
from rest_framework.reverse import reverse

from diamm.helpers.solr_helpers import SolrManager


class ImageResourceSerializer(ypres.DictSerializer):
    id = ypres.MethodField(label="@id")
    type = ypres.StaticField(label="@type", value="dctypes:Image")
    format = ypres.StaticField(value="image/jpeg")
    width = ypres.IntField(attr="width_i")
    height = ypres.IntField(attr="height_i")
    alabel = ypres.StrField(label="label", attr="image_type_s")
    service = ypres.MethodField()

    def get_id(self, obj: dict) -> str:
        return reverse(
            "image-serve-redirect",
            kwargs={"pk": obj["pk"]},
            request=self.context["request"],
        )

    def get_service(self, obj: dict) -> dict:
        proxied_image_url = reverse(
            "image-serve-redirect",
            kwargs={"pk": obj["pk"]},
            request=self.context["request"],
        )
        return {
            "@context": "http://iiif.io/api/image/2/context.json",
            "profile": "http://iiif.io/api/image/2/level1.json",
            "@id": proxied_image_url,
        }


class ImageSerializer(ypres.DictSerializer):
    type = ypres.StaticField(label="@type", value="oa:Annotation")
    motivation = ypres.StaticField(value="sc:painting")
    on = ypres.MethodField()
    resource = ypres.MethodField()

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
            conn.search("*:*", **canvas_query)

            return {
                "@type": "oa:Choice",
                "default": ImageResourceSerializer(
                    obj, context={"request": self.context["request"]}
                ).serialized,
                "item": ImageResourceSerializer(
                    conn.results,
                    many=True,
                    context={"request": self.context["request"]},
                ).serialized_many,
            }

        return ImageResourceSerializer(
            obj, context={"request": self.context["request"]}
        ).serialized
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
