import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class CountryCitySerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("country-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class ArchiveCitySerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("archive-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class CityListSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("city-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class CityDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    archives = serpy.MethodField()
    country = serpy.MethodField()
    provenance_relationships = serpy.MethodField()

    def get_archives(self, obj):
        return ArchiveCitySerializer(obj.archives.all(), many=True, context=self.context).data

    def get_country(self, obj):
        return CountryCitySerializer(obj.parent, context=self.context).data

    def get_provenance_relationships(self, obj):
        return ProvenanceSerializer(obj.city_sources.all(), many=True, context=self.context).data

    def get_url(self, obj):
        return reverse("city-detail", kwargs={"pk": obj.id}, request=self.context['request'])
