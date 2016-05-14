# This module creates a IIIF Manifest from a source object.
# There are a few things to note about this process:
#  - To optimize the response speed, the manifest is assembled via Solr,
#    not directly from the database.
#  - DIAMM Proxies the images using their primary key. This is to prevent
#    problems with loading insecure content (DIAMM is served over HTTPS, and
#    most browsers will refuse to cross-load secure and insecure content). This also
#    simplifies loading images into a canvas.
import serpy
import pysolr
from django.conf import settings
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextDictSerializer
from diamm.serializers.fields import StaticField


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


class ServiceSerializer(ContextDictSerializer):
    service = StaticField(
        label="@context",
        value="https://www.diamm.ac.uk/services/item"
    )
    id = serpy.MethodField(
        label="@id"
    )
    type = StaticField(
        value="Item"
    )

    composers = serpy.MethodField()
    voices = serpy.MethodField()
    folios = serpy.MethodField()

    def get_id(self, obj):
        return reverse('source-item-detail',
                       kwargs={"source_id": obj['source_i'],
                               "item_id": obj['pk']},
                       request=self.context['request'])

    def get_composers(self, obj):
        composers = []
        for composer in obj['composers_ssni']:
            c = {}
            name, pk, uncertain = composer.split("|")
            c['name'] = name

            if pk:
                composer_url = reverse("person-detail",
                                       kwargs={"pk": pk},
                                       request=self.context['request'])
                c["@id"] = composer_url

            if uncertain and uncertain == "True":
                c['uncertain'] = True
            else:
                c['uncertain'] = False

            composers.append(c)
        return composers

    def get_voices(self, obj):
        id_list = ",".join([str(x) for x in obj['voices_ii']])
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ["type:voice", "{!terms f=pk}"+id_list]
        sort = "sort_order_i asc"
        voice_list = connection.search("*:*", fq=fq, sort=sort, rows=100)

        if voice_list.hits == 0:
            return []

        voices = []
        for voice in voice_list.docs:
            v = {}

            v['voice_type'] = voice.get('voice_type_s')
            v['voice_text'] = voice.get('voice_text_s')
            v['languages'] = voice.get('languages_ss')  # an array of languages
            v['clef'] = voice.get('clef_s')
            v['mensuration_sign'] = voice.get('mensuration_s')
            v['mensuration_text'] = voice.get('mensuration_text_s')

            v = {key: value for key, value in v.items() if value}
            voices.append(v)

        return voices

    def get_folios(self, obj):
        if not 'pages_ii' in obj:
            return {}

        folios = {}

        folios['start'] = {
            'label': obj['folio_start_s'],
            '@id': reverse('source-canvas-detail',
                           kwargs={"source_id": obj['source_i'],
                                   "page_id": obj['pages_ii'][0]},
                           request=self.context['request'])
        }

        folios['end'] = {
            'label': obj['folio_end_s'],
            '@id': reverse('source-canvas-detail',
                           kwargs={'source_id': obj['source_i'],
                                   "page_id": obj['pages_ii'][-1]},
                           request=self.context['request'])
        }

        return folios


class StructureSerializer(ContextDictSerializer):
    canvases = serpy.MethodField()
    id = serpy.MethodField(
        label="@id"
    )
    type = StaticField(
        label="@type",
        value="sc:Range"
    )
    label = serpy.StrField(
        attr='composition_s'
    )

    service = serpy.MethodField()

    def get_canvases(self, obj):
        if not obj.get('pages_ii'):
            return []

        canvases = []
        for p in obj['pages_ii']:
            canvas_id = reverse("source-canvas-detail",
                                kwargs={"source_id": obj['source_i'],
                                "page_id": p},
                                request=self.context['request'])
            canvases.append(canvas_id)

        return canvases

    def get_id(self, obj):
        return reverse('source-range-detail',
                       kwargs={"source_id": obj['source_i'],
                               "item_id": obj['pk']},
                       request=self.context['request'])

    def get_service(self, obj):
        return ServiceSerializer(obj, context={"request": self.context['request']}).data


class ImageSerializer(ContextDictSerializer):
    type = StaticField(
        label="@type",
        value="oa:Annotation"
    )
    motivation = StaticField(
        value="sc:painting"
    )
    on = serpy.MethodField()
    resource = serpy.MethodField()

    def get_on(self, obj):
        page_id = self.context["page_id"]
        source_id = self.context["source_id"]
        request = self.context["request"]
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": source_id, "page_id": page_id},
            request=request
        )

    def get_resource(self, obj):
        proxied_image_url = reverse('image-serve-info',
                                    kwargs={"pk": obj['pk']},
                                    request=self.context['request'])
        return {
            "@id": proxied_image_url,
            "@type": "dctypes:Image",
            "format": "image/jpeg",
            "width": obj['width_i'],
            "height": obj['height_i'],
            "service": {
                "@context": "http://iiif.io/api/image/2/context.json",
                "@id": proxied_image_url,
                "profile": "http://iiif.io/api/image/2/level1.json"
            }
        }


class CanvasSerializer(ContextDictSerializer):
    id = serpy.MethodField(
        label="@id"
    )
    type = StaticField(
        value="sc:Canvas",
        label="@type"
    )
    label = serpy.StrField(
        attr="numeration_s"
    )
    images = serpy.MethodField()

    def get_id(self, obj):
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": obj['source_i'],
                    "page_id": obj['pk']},
            request=self.context['request']
        )

    def get_images(self, obj):
        if not '_childDocuments_' in obj:
            return []

        imgs = obj['_childDocuments_']
        context = {
            "source_id": obj["source_i"],
            "page_id": obj["pk"],
            "request": self.context['request']
        }
        imgs_data = [ImageSerializer(i, context=context).data for i in imgs]
        return imgs_data


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
    related = serpy.MethodField()
    sequences = serpy.MethodField()
    structures = serpy.MethodField()
    thumbnail = serpy.MethodField()

    def get_id(self, obj):
        return reverse('source-manifest',
                       kwargs={'pk': obj['pk']},
                       request=self.context['request'])

    def get_metadata(self, obj):
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

    def get_see_also(self, obj):
        source_id = obj['pk']
        source_url = reverse('source-detail',
                             kwargs={'pk': source_id},
                             request=self.context['request'])
        return {
            '@id': source_url,
            'format': "application/json"
        }

    def get_related(self, obj):
        source_id = obj['pk']
        source_url = reverse('source-detail',
                             kwargs={"pk": source_id},
                             request=self.context['request'])
        return {
            "@id": source_url,
            "format": "text/html"
        }

    def get_sequences(self, obj):
        conn = pysolr.Solr(settings.SOLR['SERVER'])

        # image_type_i:1 in the field list transformer childFilter ensures that
        # only the primary images (type 1) are returned.
        canvas_query = {
            "fq": ["type:page", "source_i:{0}".format(obj['pk'])],
            "fl": ["id", "pk", "source_i", "numeration_s", "items_ii",
                   "[child parentFilter=type:page childFilter=image_type_i:1 childFilter=type:image]"],
            "sort": "sort_order_i asc, numeration_ans asc",
            "rows": 10000
        }
        canvas_res = conn.search("*:*", **canvas_query)
        canvases = [CanvasSerializer(c, context={"request": self.context['request']}).data
                    for c in canvas_res.docs]

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

    def get_thumbnail(self, obj):
        if not 'cover_image_url_sni' in obj:
            return {}
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

    def get_structures(self, obj):
        conn = pysolr.Solr(settings.SOLR['SERVER'])

        structure_query = {
            "fq": ["type:item", "source_i:{0}".format(obj['pk'])],
            "sort": "folio_start_ans asc",
            "rows": 10000,
        }
        structure_res = conn.search("*:*", **structure_query)
        structures = [StructureSerializer(s, context={"request": self.context["request"]}).data
                      for s in structure_res.docs]

        return structures
