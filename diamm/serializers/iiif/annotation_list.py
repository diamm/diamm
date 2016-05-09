import serpy
import pysolr
from django.conf import settings
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextDictSerializer
from diamm.serializers.fields import StaticField


class AnnotationVoiceSerializer(ContextDictSerializer):
    type = serpy.StrField(
        attr='voice_type_s'
    )
    text = serpy.MethodField()
    languages = serpy.MethodField()
    clef = serpy.MethodField()
    mensuration = serpy.MethodField()
    mensuration_text = serpy.MethodField()

    def get_text(self, obj):
        if 'voice_text_s' in obj:
            return obj['voice_text_s']
        return None

    def get_clef(self, obj):
        if 'clef_s' in obj:
            return obj['clef_s']
        return None

    def get_mensuration(self, obj):
        if 'mensuration_s' in obj:
            return obj['mensuration_s']
        return None

    def get_mensuration_text(self, obj):
        if 'mensuration_text_s' in obj:
            return obj['mensuation_text_s']
        return None

    def get_languages(self, obj):
        if 'languages_ss' in obj:
            return obj['languages_ss']
        return []


class AnnotationSerializer(ContextDictSerializer):
    type = StaticField(
        value="oa:Annotation",
        label="@type"
    )
    motivation = StaticField(
        value="sc:painting"
    )
    resource = serpy.MethodField()

    def get_resource(self, obj):
        body = {}

        body['voices'] = self._get_voice_data(obj)

        if 'folio_start_s' in obj:
            body['folio_start'] = obj['folio_start_s']

        if 'folio_end_s' in obj:
            body['folio_end'] = obj['folio_end_s']

        if 'composition_s' in obj:
            composition = {
                "name": obj['composition_s']
            }
            if 'composition_i' in obj:
                composition_url = reverse(
                    'composition-detail',
                    kwargs={"pk": obj['composition_i']},
                    request=self.context['request']
                )
                composition.update({
                    "@id": composition_url
                })
            body.update({"composition": composition})

        if 'composers_ssni' in obj:
            composers = []
            body.update({"composers": composers})
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

        return {
            "@id": "",
            "@type": ["dctypes:Dataset", "cnt:ContentAsText"],
            "format": "application/json",
            "chars": body
        }

    def _get_voice_data(self, obj):
        if not 'voices_ii' in obj:
            return None

        id_list = ",".join([str(x) for x in obj['voices_ii']])
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ["type:voice", "{!terms f=pk}"+id_list]
        sort = "sort_order_i asc"
        voice_list = connection.search("*:*", fq=fq, sort=sort, rows=100)

        if voice_list.hits == 0:
            return []

        serialized = AnnotationVoiceSerializer(voice_list.docs, many=True).data
        return serialized



class AnnotationListSerializer(ContextDictSerializer):
    ctx = StaticField(
        value="http://iiif.io/api/presentation/2/context.json",
        label="@context"
    )
    id = serpy.MethodField(
        label="@id"
    )
    type = StaticField(
        value="sc:AnnotationList",
        label="@type"
    )
    resources = serpy.MethodField()

    def get_id(self, obj):
        kwargs = {
            "source_id": self.context["source_id"],
            "page_id": self.context["page_id"]
        }
        return reverse("source-canvas-annotations",
                       kwargs=kwargs,
                       request=self.context['request'])

    def get_resources(self, obj):
        context = {
            "source_id": self.context['source_id'],
            "page_id": self.context['page_id'],
            "request": self.context['request']
        }
        return AnnotationSerializer(obj,
                                    many=True,
                                    context=context).data
