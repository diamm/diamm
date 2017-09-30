import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class CountryStateSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("country-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class CountryRegionSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("region-detail", kwargs={"pk": obj.id}, request=self.context['request'])


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
    pk = serpy.IntField()
    name = serpy.StrField()
    cities = serpy.MethodField()
    regions = serpy.MethodField()
    states = serpy.MethodField()
    provenance_relationships = serpy.MethodField()

    def get_cities(self, obj):
        return CountryCitySerializer(obj.cities.select_related('parent').order_by('name'),
                                     many=True,
                                     context=self.context).data

    def get_regions(self, obj):
        return CountryRegionSerializer(obj.regions.select_related('parent').order_by('name'),
                                       many=True,
                                       context=self.context).data

    def get_states(self, obj):
        return CountryStateSerializer(obj.states.select_related('parent').order_by('name'),
                                      many=True,
                                      context=self.context).data

    def get_url(self, obj):
        return reverse("country-detail", kwargs={"pk": obj.id}, request=self.context['request'])

    def get_provenance_relationships(self, obj):
        pass
