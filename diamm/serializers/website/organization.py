from rest_framework import serializers
from diamm.models.data.organization import Organization


class OrganizationListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ('url', 'name')


class OrganizationDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ('url', 'name')
