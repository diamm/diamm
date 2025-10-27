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

from diamm.helpers.solr_helpers import SolrManager
from diamm.serializers.iiif.canvas import CanvasSerializer
from diamm.serializers.iiif.helpers import create_metadata_block
from diamm.serializers.iiif.structure import StructureSerializer


class SourceManifestSerializer(ypres.DictSerializer):
    ctx = ypres.StaticField(
        value="http://iiif.io/api/presentation/2/context.json", label="@context"
    )
    id = ypres.MethodField(label="@id")
    type = ypres.StaticField(value="sc:Manifest", label="@type")
    label_ = ypres.StrField(label="label", attr="display_name_s")
    metadata = ypres.MethodField()
    see_also = ypres.MethodField(label="seeAlso")
    description = ypres.MethodField()

    related = ypres.MethodField()
    sequences = ypres.MethodField()
    structures = ypres.MethodField()
    attribution = ypres.StaticField(value="Digital Image Archive of Medieval Music")

    logo = ypres.StaticField(
        value=f"https://{settings.HOSTNAME}/static/images/diammlogo.png"
    )

    thumbnail = ypres.MethodField(required=False)

    def get_id(self, obj: dict) -> str:
        return reverse(
            "source-manifest", kwargs={"pk": obj["pk"]}, request=self.context["request"]
        )

    def get_metadata(self, obj: dict) -> list:  # noqa: UP006
        return create_metadata_block(obj)

    def get_description(self, obj: dict) -> str | None:
        if "notes_txt" in obj:
            # return the first note for the description. Truncate it to 300 words
            return truncatewords(obj["notes_txt"][0], 300)
        return None

    def get_see_also(self, obj: dict) -> dict:
        source_id = obj["pk"]
        source_url = reverse(
            "source-detail", kwargs={"pk": source_id}, request=self.context["request"]
        )
        return {"@id": source_url, "format": "application/json"}

    def get_related(self, obj: dict) -> dict:
        source_id = obj["pk"]
        source_url = reverse(
            "source-detail", kwargs={"pk": source_id}, request=self.context["request"]
        )
        return {"@id": source_url, "format": "text/html"}

    def get_sequences(self, obj: dict) -> list:
        conn = SolrManager(settings.SOLR["SERVER"])

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

        label = "Default"
        source_id = obj["pk"]
        source_url = reverse(
            "source-manifest", kwargs={"pk": source_id}, request=self.context["request"]
        )
        sequence_id = f"{source_url}sequence/{label.lower()}"

        return [
            {
                "@id": sequence_id,
                "@type": "sc:Sequence",
                "label": label,
                "canvases": canvases,
            }
        ]

    def get_thumbnail(self, obj: dict) -> dict | None:
        if "cover_image_url_sni" not in obj:
            return None
        else:
            cover_image_url = reverse(
                "image-serve-info",
                kwargs={"pk": obj["cover_image_i"]},
                request=self.context["request"],
            )
            return {
                "@id": cover_image_url
                + f"full/{settings.IIIF['THUMBNAIL_WIDTH']},/0/default.jpg",
                "service": {
                    "@context": "http://iiif.io/api/image/2/context.json",
                    "@id": cover_image_url,
                    "profile": "http://iiif.io/api/image/2/level1.json",
                },
            }

    def get_structures(self, obj: dict) -> list:
        conn = SolrManager(settings.SOLR["SERVER"])

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
