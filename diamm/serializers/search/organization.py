from rest_framework import serializers
from diamm.models.data.organization import Organization


class OrganizationSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("type",
                  "pk",
                  "name_s",
                  "location_s")

    # TODO: Find some way to refactor these into a base class for DRY
    type = serializers.SerializerMethodField()
    pk = serializers.ReadOnlyField()

    name_s = serializers.ReadOnlyField(source="name")
    location_s = serializers.ReadOnlyField(source="location.name")

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()
