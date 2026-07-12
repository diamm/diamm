# This module creates a IIIF Manifest from a source object.
# There are a few things to note about this process:
#  - To optimize the response speed, the manifest is assembled via Solr,
#    not directly from the database.
#  - DIAMM Proxies the images using their primary key. This is to prevent
#    problems with loading insecure content (DIAMM is served over HTTPS, and
#    most browsers will refuse to cross-load secure and insecure content). This also
#    simplifies loading images into a canvas.

import ypres
from django.conf import settings
from django.template.defaultfilters import truncatewords
from rest_framework.reverse import reverse

from diamm.helpers.solr import SolrManager
from diamm.serializers.iiif.canvas import CanvasSerializer
from diamm.serializers.iiif.helpers import create_metadata_block, language_map
from diamm.serializers.iiif.structure import StructureSerializer


class SourceManifestSerializer(ypres.DictSerializer):
    ctx = ypres.StaticField(
        value="http://iiif.io/api/presentation/3/context.json", label="@context"
    )
    id = ypres.MethodField()
    type = ypres.StaticField(value="Manifest")
    label = ypres.MethodField()
    metadata = ypres.MethodField()
    see_also = ypres.MethodField(label="seeAlso")
    summary = ypres.MethodField()
    homepage = ypres.MethodField()
    items = ypres.MethodField()
    structures = ypres.MethodField()
    required_statement = ypres.MethodField(label="requiredStatement")
    provider = ypres.MethodField()
    thumbnail = ypres.MethodField(required=False)

    def get_id(self, obj: dict) -> str:
        return reverse(
            "source-manifest", kwargs={"pk": obj["pk"]}, request=self.context["request"]
        )

    def get_label(self, obj: dict) -> dict:
        return language_map(obj["display_name_s"])

    def get_metadata(self, obj: dict) -> list:  # noqa: UP006
        return create_metadata_block(obj)

    def get_summary(self, obj: dict) -> dict | None:
        if "notes_txt" in obj:
            # return the first note for the description. Truncate it to 300 words
            return language_map(truncatewords(obj["notes_txt"][0], 300))
        return None

    def get_see_also(self, obj: dict) -> list[dict]:
        source_id = obj["pk"]
        source_url = reverse(
            "source-detail", kwargs={"pk": source_id}, request=self.context["request"]
        )
        return [{"id": source_url, "type": "Dataset", "format": "application/json"}]

    def get_homepage(self, obj: dict) -> list[dict]:
        source_id = obj["pk"]
        source_url = reverse(
            "source-detail", kwargs={"pk": source_id}, request=self.context["request"]
        )
        return [
            {
                "id": source_url,
                "type": "Text",
                "format": "text/html",
                "label": language_map(obj["display_name_s"]),
            }
        ]

    def get_required_statement(self, obj: dict) -> dict:
        del obj
        return {
            "label": language_map("Attribution", "en"),
            "value": language_map("Digital Image Archive of Medieval Music"),
        }

    def get_provider(self, obj: dict) -> list[dict]:
        del obj
        return [
            {
                "id": f"https://{settings.HOSTNAME}/",
                "type": "Agent",
                "label": language_map("Digital Image Archive of Medieval Music", "en"),
                "homepage": [
                    {
                        "id": f"https://{settings.HOSTNAME}/",
                        "type": "Text",
                        "format": "text/html",
                        "label": language_map(
                            "Digital Image Archive of Medieval Music", "en"
                        ),
                    }
                ],
                "logo": [
                    {
                        "id": f"https://{settings.HOSTNAME}/static/images/diammlogo.png",
                        "type": "Image",
                        "format": "image/png",
                    }
                ],
            }
        ]

    def get_items(self, obj: dict) -> list:
        conn = SolrManager()

        # image_type_i:1 in the field list transformer childFilter ensures that
        # only the primary images (type 1) are returned.
        # images_ss:[* TO *] ensures that only records with images attached are returned.
        canvas_query = {
            "fq": ["type:image", f"source_i:{obj['pk']}", "image_type_i:1"],
            "sort": "sort_order_f asc, numeration_ans asc",
        }
        conn.search("*:*", **canvas_query)

        canvases = CanvasSerializer(
            conn.results, many=True, context={"request": self.context["request"]}
        ).serialized_many

        return canvases

    def get_thumbnail(self, obj: dict) -> list[dict] | None:
        if "cover_image_url_sni" not in obj:
            return None
        else:
            cover_image_service_url = reverse(
                "image-serve-redirect",
                kwargs={"pk": obj["cover_image_i"]},
                request=self.context["request"],
            )
            return [
                {
                    "id": cover_image_service_url
                    + f"full/{settings.IIIF['THUMBNAIL_WIDTH']}/0/default.jpg",
                    "type": "Image",
                    "format": "image/jpeg",
                    "service": [
                        {
                            "id": cover_image_service_url,
                            "type": "ImageService2",
                            "profile": "level1",
                        }
                    ],
                }
            ]

    def get_structures(self, obj: dict) -> list:
        conn = SolrManager()

        # The pages_ii query ensures we retrieve only those records that have images associated with them.
        structure_query = {
            "fq": ["type:item", f"source_i:{obj['pk']}", "pages_ii:[* TO *]"],
            "sort": "folio_start_ans asc",
            "rows": 100,
        }
        conn.search("*:*", **structure_query)

        return StructureSerializer(
            conn.results, context={"request": self.context["request"]}, many=True
        ).serialized_many
