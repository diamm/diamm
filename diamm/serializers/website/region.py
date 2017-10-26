import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class RegionCitySerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse('city-detail', kwargs={"pk": obj.id}, request=self.context['request'])


class RegionOrganizationSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse('organization-detail', kwargs={"pk": obj.id}, request=self.context['request'])


class RegionProvenanceSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.MethodField()
    region_uncertain = serpy.BoolField()
    earliest_year = serpy.IntField()
    latest_year = serpy.IntField()

    def get_url(self, obj):
        return reverse('source-detail', kwargs={"pk": obj.source.id}, request=self.context['request'])

    def get_name(self, obj):
        return "{0}".format(obj.source.display_name)


class RegionDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    pk = serpy.IntField()
    name = serpy.StrField()
    parent = serpy.StrField()
    organizations = serpy.MethodField()
    cities = serpy.MethodField()
    provenance = serpy.MethodField()

    def get_organizations(self, obj):
        return RegionOrganizationSerializer(obj.organizations.all(),
                                            many=True,
                                            context=self.context).data

    def get_cities(self, obj):
        return RegionCitySerializer(obj.cities.select_related('parent'),
                                    many=True,
                                    context=self.context).data

    def get_provenance(self, obj):
        return RegionProvenanceSerializer(obj.region_sources.select_related('source'),
                                          many=True,
                                          context=self.context).data

    def get_url(self, obj):
        return reverse("region-detail", kwargs={"pk": obj.id}, request=self.context['request'])
