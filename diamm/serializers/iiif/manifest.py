# This module creates a IIIF Manifest from a source object.
# There are a few things to note about this process:
#  - To optimize the response speed, the manifest is assembled via Solr,
#    not directly from the database.
#  - DIAMM Proxies the images using their primary key. This is to prevent
#    problems with loading insecure content (DIAMM is served over HTTPS, and
#    most browsers will refuse to cross-load secure and insecure content). This also
#    simplifies loading images into a canvas.
from typing import List, Dict, Optional
import serpy
from django.conf import settings
from django.template.defaultfilters import truncatewords
from rest_framework.reverse import reverse

from diamm.helpers.solr_helpers import SolrManager
from diamm.serializers.fields import StaticField
from diamm.serializers.iiif.canvas import CanvasSerializer
from diamm.serializers.iiif.structure import StructureSerializer
from diamm.serializers.serializers import ContextDictSerializer

METADATA_MAPPING = {
    'name_s': 'Name',
    'shelfmark_s': 'Shelfmark',
    'archive_s': 'Archive',
    'surface_type_s': 'Surface Type',
    'measurements_s': 'Measurements',
    'identifiers_ss': 'Identifiers',
    'date_statement_s': 'Date Statement',
    'source_type_s': 'Source Type'
}


class SourceManifestSerializer(ContextDictSerializer):
    ctx = StaticField(
        value="http://iiif.io/api/presentation/2/context.json",
        label="@context"
    )
    id = serpy.MethodField(
        label="@id"
    )
    type = StaticField(
        value="sc:Manifest",
        label="@type"
    )
    label = serpy.StrField(
        attr="display_name_s"
    )
    metadata = serpy.MethodField()
    see_also = serpy.MethodField(
        label="seeAlso"
    )
    description = serpy.MethodField()

    related = serpy.MethodField()
    sequences = serpy.MethodField()
    structures = serpy.MethodField()
    attribution = StaticField(
        value="Digital Image Archive of Medieval Music"
    )

    logo = StaticField(
        value="https://{0}/static/images/diammlogo.png".format(settings.HOSTNAME)
    )

    thumbnail = serpy.MethodField(
        required=False
    )

    def get_id(self, obj: Dict) -> str:
        return reverse('source-manifest',
                       kwargs={'pk': obj['pk']},
                       request=self.context['request'])

    def get_metadata(self, obj: Dict) -> List:
        metadata_entries = []
        for field, label in METADATA_MAPPING.items():
            if field not in obj:
                continue

            value = obj[field]
            if isinstance(value, list):
                for v in value:
                    metadata_entries.append({
                        'label': label,
                        'value': v
                    })
            else:
                metadata_entries.append({
                    'label': label,
                    'value': value
                })
        return metadata_entries

    def get_description(self, obj: Dict) -> Optional[str]:
        if 'notes_txt' in obj:
            # return the first note for the description. Truncate it to 300 words
            return truncatewords(obj['notes_txt'][0], 300)
        return None

    def get_see_also(self, obj: Dict) -> Dict:
        source_id = obj['pk']
        source_url = reverse('source-detail',
                             kwargs={'pk': source_id},
                             request=self.context['request'])
        return {
            '@id': source_url,
            'format': "application/json"
        }

    def get_related(self, obj: Dict) -> Dict:
        source_id = obj['pk']
        source_url = reverse('source-detail',
                             kwargs={"pk": source_id},
                             request=self.context['request'])
        return {
            "@id": source_url,
            "format": "text/html"
        }

    def get_sequences(self, obj: Dict) -> List:
        conn = SolrManager(settings.SOLR['SERVER'])

        # image_type_i:1 in the field list transformer childFilter ensures that
        # only the primary images (type 1) are returned.
        # images_ss:[* TO *] ensures that only records with images attached are returned.
        canvas_query = {
            "fq": ["type:page", "source_i:{0}".format(obj['pk']), "images_ss:[* TO *]"],
            "fl": ["id", "pk", "source_i", "numeration_s", "items_ii", "page_type_i",
                   "[child parentFilter=type:page childFilter=type:image]"],
            "sort": "sort_order_i asc, image_type_i asc, numeration_ans asc",
            "rows": 100
        }
        conn.search("*:*", **canvas_query)

        canvases = CanvasSerializer(conn.results, many=True, context={"request": self.context['request']}).data

        label = "Default"
        source_id = obj['pk']
        source_url = reverse('source-manifest',
                             kwargs={'pk': source_id},
                             request=self.context['request'])
        sequence_id = "{0}sequence/{1}".format(source_url, label.lower())

        return [{
            "@id": sequence_id,
            "@type": "sc:Sequence",
            "label": label,
            "canvases": canvases
        }]

    def get_thumbnail(self, obj: Dict) -> Optional[Dict]:
        if 'cover_image_url_sni' not in obj:
            return None
        else:
            cover_image_url = reverse('image-serve-info',
                                      kwargs={"pk": obj['cover_image_i']},
                                      request=self.context['request'])
            return {
                "@id": cover_image_url + "full/{0},/0/default.jpg".format(settings.IIIF['THUMBNAIL_WIDTH']),
                "service": {
                    "@context": "http://iiif.io/api/image/2/context.json",
                    "@id": cover_image_url,
                    "profile": "http://iiif.io/api/image/2/level1.json"
                }
            }

    def get_structures(self, obj: Dict) -> List:
        conn = SolrManager(settings.SOLR['SERVER'])

        # The pages_ii query ensures we retrieve only those records that have images associated with them.
        structure_query = {
            "fq": ["type:item", "source_i:{0}".format(obj['pk']), "pages_ii:[* TO *]"],
            "fl": ["pages_ii", "pages_ssni", "source_i", "pk", "composition_s"],
            "sort": "folio_start_ans asc",
            "rows": 100,
        }
        conn.search("*:*", **structure_query)

        structures = StructureSerializer(conn.results,
                                         context={"request": self.context["request"]},
                                         many=True).data

        return structures
