import serpy

from diamm.models.data.geographic_area import GeographicArea
from diamm.serializers.serializers import HyperlinkedContextSerializer


class CountryCitySerializer(HyperlinkedContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return self.generate_url('country-detail', obj.pk)

class ArchiveCitySerializer(HyperlinkedContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return self.generate_url('archive-detail', obj.pk)

class CityListSerializer(HyperlinkedContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return self.generate_url('city-detail', obj.pk)

class CityDetailSerializer(HyperlinkedContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    archives = serpy.MethodField()
    country = serpy.MethodField()

    def get_archives(self, obj):
        return ArchiveCitySerializer(obj.archives.all(), many=True, context=self.context).data

    def get_country(self, obj):
        return CountryCitySerializer(obj.parent, context=self.context).data

    def get_url(self, obj):
        return self.generate_url('city-detail', obj.pk)
