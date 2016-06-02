from rest_framework import serializers
from diamm.models.data.organization import Organization


class OrganizationListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ('url', 'name')


class OrganizationDetailSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.SerializerMethodField()
    pk = serializers.IntegerField()

    class Meta:
        model = Organization
        fields = ('url', 'name', 'type', 'pk')

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()
