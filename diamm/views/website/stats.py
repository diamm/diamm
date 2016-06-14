import pysolr
import serpy
from django.conf import settings
from rest_framework import generics
from rest_framework import response
from diamm.serializers.website.stats import StatsSerializer 

class StatsView(generics.GenericAPIView):
    template_name = ""

    def get(self, request, *args, **kwargs):
        conn = pysolr.Solr(settings.SOLR['SERVER'])
        results = conn.search("*:*", rows=0, facet='on', **{ 'facet.field' : 'type' })
        i = iter(results.facets['facet_fields']['type'])
        # contains a dictinary with the count of types, keys include:
            # person, voice, item, sourcerelationship, set, organization, itembibliography, 
            # image, source, bibliography, composition, archive, page, sourceprovenance, sourcecopyist
        type_counts = dict(zip(i, i))

        results = conn.search("*:*", rows=0, fq=['public_images_b:true'])
        type_counts['source_with_images'] = results.hits

        res = StatsSerializer(type_counts)
        return response.Response(res.data)
