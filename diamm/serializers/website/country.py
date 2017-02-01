import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer
from diamm.serializers.website.provenance import ProvenanceSerializer


class CountryCitySerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("city-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class CountryListSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("country-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class CountryDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    cities = serpy.MethodField()
    regions = serpy.MethodField()
    provenance_relationships = serpy.MethodField()

    def get_cities(self, obj):
        return CountryCitySerializer(obj.cities.all(), many=True, context=self.context).data

    def get_regions(self, obj):
        return obj.regions.values_list('name', flat=True)

    def get_url(self, obj):
        return reverse("country-detail", kwargs={"pk": obj.id}, request=self.context['request'])

    def get_provenance_relationships(self, obj):
        pass
