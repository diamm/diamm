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
        value="https://{0}/services/item".format(settings.HOSTNAME)
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
