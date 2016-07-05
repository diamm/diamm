from rest_framework import serializers
from rest_framework.reverse import reverse
import pysolr

from django.conf import settings
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.archive import Archive


class CountryCitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GeographicArea
        fields = ('url', 'name')
        extra_kwargs = {
            'url': {'view_name': 'country-detail'}
        }


class ArchiveCitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Archive
        fields = ('url', 'name')


class CityListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='city-detail')

    class Meta:
        model = GeographicArea
        fields = ('url', 'name')


class CityDetailSerializer(serializers.HyperlinkedModelSerializer):
    archives = ArchiveCitySerializer(many=True)
    country = CountryCitySerializer(
        source='parent'
    )
    sources = serializers.SerializerMethodField() 

    class Meta:
        model = GeographicArea
        fields = ('url', 'name', 'archives', 'country', 'sources')
        extra_kwargs = {
            'url': {'view_name': 'city-detail'}
        }

    def get_sources(self, obj):
        sources = list()
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:source', 'geographic_area_ii:' + str(obj.id)]
        results = connection.search('*:*', fq=fq)
        if results.hits > 0:
            for doc in results.docs:
                sources.append({
                    'url': 
                        reverse(
                            'source-detail', 
                            kwargs={'pk': doc['pk']},
                            request=self.context['request']),
                    'name': doc['display_name_s']
                })
        return sources 

