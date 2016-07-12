import serpy
from rest_framework.reverse import reverse

from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.archive import Archive
from diamm.serializers.serializers import ContextSerializer


class CountryCitySerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    #TODO: find a way to factor this url method out in a more DRY way
    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(reverse('country-detail', [obj.pk]))

class ArchiveCitySerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(reverse('archive-detail', [obj.pk]))

class CityListSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(reverse('city-detail', [obj.pk]))

class CityDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    archives = serpy.MethodField()
    country = serpy.MethodField()

    def get_archives(self, obj):
        return ArchiveCitySerializer(obj.archives.all(), many=True, context=self.context).data

    def get_country(self, obj):
        return CountryCitySerializer(obj.parent, context=self.context).data

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(reverse('city-detail', [obj.pk]))
