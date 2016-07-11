import pysolr
from django.conf import settings
from rest_framework import generics
from rest_framework import response
from diamm.serializers.website.stats import StatsSerializer
from diamm.models.data.item_composer import ItemComposer


class StatsView(generics.GenericAPIView):
    template_name = "website/stats/stats.jinja2"

    def get(self, request, *args, **kwargs):
        conn = pysolr.Solr(settings.SOLR['SERVER'])
        q = {
            "rows": 0,
            "facet": 'on',
            "facet.field": "type"
        }
        type_results = conn.search("*:*", **q)
        import pdb
        pdb.set_trace()
        i = iter(type_results.facets['facet_fields']['type'])
        # contains a dictionary with the count of types, keys include:
        # person, voice, item, sourcerelationship, set, organization, itembibliography,
        # image, source, bibliography, composition, archive, page, sourceprovenance, sourcecopyist
        type_counts = dict(zip(i, i))

        source_results = conn.search("*:*", rows=0, fq=['public_images_b:true'])
        type_counts['source_with_images'] = source_results.hits

        composers = ItemComposer.objects.values('composer').distinct().count()
        type_counts['composer'] = composers

        res = StatsSerializer(type_counts).data
        return response.Response(res)
