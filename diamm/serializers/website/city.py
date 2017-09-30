import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class CityProvenanceSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.MethodField()
    city_uncertain = serpy.BoolField()
    earliest_year = serpy.IntField()
    latest_year = serpy.IntField()

    def get_url(self, obj):
        return reverse('source-detail', kwargs={"pk": obj.source.id}, request=self.context['request'])

    def get_name(self, obj):
        return "{0}".format(obj.source.display_name)


class OrganizationSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse('organization-detail', kwargs={"pk": obj.id}, request=self.context['request'])


class CountryCitySerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("country-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class ArchiveCitySerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    siglum = serpy.StrField()

    def get_url(self, obj):
        return reverse("archive-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class CityListSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse("city-detail", kwargs={"pk": obj.id}, request=self.context['request'])


class CityDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    pk = serpy.IntField()
    name = serpy.StrField()
    archives = serpy.MethodField()
    country = serpy.MethodField()
    # provenance_relationships = serpy.MethodField()
    organizations = serpy.MethodField()
    provenance = serpy.MethodField()
    variant_names = serpy.StrField(
        required=False
    )

    def get_archives(self, obj):
        return ArchiveCitySerializer(obj.archives.all(), many=True, context=self.context).data

    def get_country(self, obj):
        return CountryCitySerializer(obj.parent, context=self.context).data

    # def get_provenance_relationships(self, obj):
    #     return ProvenanceSerializer(obj.city_sources.all(), many=True, context=self.context).data

    def get_organizations(self, obj):
        return OrganizationSerializer(obj.organizations.all(),
                                      many=True,
                                      context=self.context).data

    def get_provenance(self, obj):
        return CityProvenanceSerializer(obj.city_sources.all(),
                                     many=True,
                                     context=self.context).data

    def get_url(self, obj):
        return reverse("city-detail", kwargs={"pk": obj.id}, request=self.context['request'])
