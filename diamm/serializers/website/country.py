from rest_framework import serializers
from diamm.models.data.geographic_area import GeographicArea


class CountryCitySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="city-detail")

    class Meta:
        model = GeographicArea
        fields = ('url', 'name')


class CountryListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="country-detail")

    class Meta:
        model = GeographicArea
        fields = ('url', 'name')


class CountryDetailSerializer(serializers.HyperlinkedModelSerializer):
    cities = CountryCitySerializer(many=True)

    class Meta:
        model = GeographicArea
        fields = ('url', 'name', 'cities')
        extra_kwargs = {
            'url': {'view_name': 'country-detail'}
        }
