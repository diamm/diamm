from rest_framework import serializers
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
        source="parent"
    )

    class Meta:
        model = GeographicArea
        fields = ('url', 'name', 'archives', 'country')
        extra_kwargs = {
            'url': {'view_name': 'city-detail'}
        }
