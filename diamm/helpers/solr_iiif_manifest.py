import pysolr
from collections import namedtuple, OrderedDict
import serpy
from django.conf import settings
from rest_framework.reverse import reverse
from diamm.serializers.iiif.ldserializer import LDSerializer
from diamm.serializers.iiif.ldfields import LDKeywordField

# Build a IIIF Manifest from a bunch of Solr Queries.
# Cache the manifest back in Solr afterwards.

class IIIFManifest:
    def __init__(self, source_id, request):
        self.request = request
        self.source_id = source_id
        self.conn = pysolr.Solr(settings.SOLR['SERVER'])

    def get(self):
        return self._fetch_or_build()

    def _fetch_or_build(self):
        manifest = self.conn.search("*:*",
                                    fq=['type:iiifmanifest', 'pk:{0}'.format(self.source_id)],
                                    fl=['manifest_sni'])
        if manifest.hits == 0:
            return self._build_and_cache_manifest()
        elif manifest.hits > 1:
            #   do something intelligent?
            pass
        else:
            return manifest.docs[0]['manifest_sni']

    def _build_and_cache_manifest(self):
        self._fetch_source_metadata()

        manifest = OrderedDict([
            ("@context", "http://iiif.io/api/presentation/2/context.json"),
            ("@id", self._build_id()),
            ("@type", "sc:Manifest"),
            ("label", self.source_result['name_s']),   # All sources should have a name.
            ("metadata", self._build_metadata()),
            ("seeAlso", reverse('source-detail', kwargs={"pk": self.source_id}, request=self.request)),
            ("sequences", self._build_sequences())
        ])
        return manifest

    def _fetch_source_metadata(self):
        # Define source fields to only fetch the ones we want (saves both bandwidth and problems with field names when
        #  converting from Solr.
        source_fields = [
            'pk',
            'name_s',
            'shelfmark_s',
            'archive_s',
            'surface_type_s',
            'measurements_s',
            'identifiers_ss',
            'date_statement_s',
            'source_type_s'
        ]
        source = self.conn.search("*:*", fq=["type:source", "pk:{0}".format(self.source_id)], fl=source_fields)

        # ensure one and only one result.
        if source.hits == 0:
            # No source was found with that ID. Bail.
            return None
        if source.hits > 1:
            raise("Expected 1 source, got {0}!".format(source.hits))

        self.source_result = source.docs[0]

    def _build_metadata(self):
        metadata_fields = (
            ('Name', 'name_s'),
            ('Shelfmark', 'shelfmark_s'),
            ('Archive', 'archive_s'),
            ('Surface Type', 'surface_type_s'),
            ('Measurements', 'measurements_s'),
            ('Identifiers', 'identifiers_ss'),
            ('Date Statement', 'date_statement_s'),
            ('Source Type', 'source_type_s')
        )

        metadata_entries = []
        for label, field in metadata_fields:
            # not all sources have all fields.
            if field not in self.source_result:
                continue
            value = self.source_result[field]

            if isinstance(value, list):
                for obj in value:
                    metadata_entries.append({
                        'label': label,
                        'value': obj
                    })
            else:
                metadata_entries.append({
                    'label': label,
                    'value': value
                })
        return metadata_entries

    def _build_id(self):
        print(self.request.build_absolute_uri())
        return self.request.build_absolute_uri()

    def _build_sequences(self):
        label = "Default"
        seq_id = self._build_id() + "sequence/{0}".format(label.lower())
        return [
            OrderedDict([
                ('@id', seq_id),
                ('@type', "sc:Sequence"),
                ("label", "Default"),
                ("canvases", self._build_canvases())
            ])
        ]

    def _build_canvases(self):
        self._fetch_canvases()
        canvases = []
        for canvas in self.page_result:
            canvases.append(OrderedDict([
                                ("@id", self._build_id() + "canvas/{0}".format(canvas['id'])),
                                ("@type", "sc:Canvas"),
                                ("label", canvas['numeration_s']),
                                ("images", self._build_images(canvas))
                            ]))
        return canvases

    def _build_images(self, canvas):
        images = []
        if '_childDocuments_' not in canvas:
            return images

        canvas_id = self._build_id() + "canvas/{0}".format(canvas['id'])
        for image in canvas['_childDocuments_']:
            images.append(OrderedDict([
                ("@type", "oa:Annotation"),
                ("on", canvas_id),
                ("resource", OrderedDict([
                    ("@id", image['location_s'] + "/full/full/0/default.jpg"),
                    ("@type", "dctypes:Image"),
                    ("format", "image/jpeg"),
                    ("width", image['width_i']),
                    ("height", image['height_i']),
                    ("service", OrderedDict([
                        ("@context", "http://iiif.io/api/image/2/context.json"),
                        ("@id", image['location_s']),
                        ("profile", "http://iiif.io/api/image/2/level1.json")
                    ]))
                ]))
            ]))

        return images

    def _fetch_canvases(self):
        """
            Fetches pages ("canvases") and images in one go.
        """
        page_fields = [
            "id",
            "numeration_s",
            "[child parentFilter=type:page childFilter=type:image]"
        ]
        pages = self.conn.search("*:*",
                                 fq=["type:page", "source_i:{0}".format(self.source_id)],
                                 fl=page_fields,
                                 sort="numeration_ans asc",
                                 rows=2000)

        self.page_result = pages.docs
