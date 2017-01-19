import serpy
import pysolr
from django.conf import settings
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextDictSerializer
from diamm.serializers.fields import StaticField


class StructureServiceSerializer(ContextDictSerializer):
    """
        A minimal serializer that returns the context and a resolvable
        @id for retrieving expanded service information.
    """
    service = StaticField(
        label="@context",
        value="https://{0}/services/item".format(settings.HOSTNAME)
    )
    id = serpy.MethodField(
        label="@id"
    )

    def get_id(self, obj):
        return reverse('source-item-detail',
                       kwargs={"source_id": obj['source_i'],
                               "item_id": obj['pk']},
                       request=self.context['request'])


class ServiceSerializer(ContextDictSerializer):
    service = StaticField(
        label="@context",
        value="https://{0}/services/item".format(settings.HOSTNAME)  # custom DIAMM service namespace
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
    composition = serpy.MethodField()
    pages = serpy.MethodField()

    def get_id(self, obj):
        return reverse('source-item-detail',
                       kwargs={"source_id": obj['source_i'],
                               "item_id": obj['pk']},
                       request=self.context['request'])

    def get_composers(self, obj):
        if 'composers_ssni' not in obj:
            return []

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
            v = {
                'voice_type': voice.get('voice_type_s'),
                'voice_text': voice.get('voice_text_s'),
                'languages': voice.get('languages_ss'),
                'clef': voice.get('clef_s'),
                'mensuration_sign': voice.get('mensuration_s'),
                'mensuration_text': voice.get('mensuration_text_s')
            }
            # strip out any None values.
            v = {key: value for key, value in v.items() if value}
            voices.append(v)

        return voices

    def get_folios(self, obj):
        folios = {}

        if 'folio_start_s' in obj:
            folios['start'] = {
                'label': obj['folio_start_s'],
                '@id': reverse('source-canvas-detail',
                               kwargs={"source_id": obj['source_i'],
                                       "page_id": obj['pages_ii'][0]},
                               request=self.context['request'])
            }

        if 'folio_end_s' in obj:
            folios['end'] = {
                'label': obj['folio_end_s'],
                '@id': reverse('source-canvas-detail',
                               kwargs={'source_id': obj['source_i'],
                                       "page_id": obj['pages_ii'][-1]},
                               request=self.context['request'])
            }

        return folios

    def get_composition(self, obj):
        if 'composition_i' in obj:
            composition = {
                'title': obj['composition_s'],
                'genres': obj.get('genres_ss'),
                '@id': reverse('composition-detail',
                                kwargs={'pk': obj['composition_i']},
                                request=self.context['request'])
            }
            return composition
        return None

    def get_pages(self, obj):
        if 'pages_ssni' in obj:
            pages = []
            for page in obj['pages_ssni']:
                pk, label = page.split("|")
                pages.append({
                    'label': label,
                    '@id': reverse('source-canvas-detail',
                                   kwargs={'source_id': obj['source_i'],
                                           "page_id": pk},
                                   request=self.context['request'])
                })
            return pages
        return None
