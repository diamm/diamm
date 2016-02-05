from django.core.urlresolvers import reverse
from rest_framework import serializers
from diamm.models.data.archive import Archive


class ArchiveSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = ("type",
                  "pk",
                  "sources_ss",
                  "city_s",
                  "name_s",
                  "country_s",
                  "siglum_s")

    # TODO: Find some way to refactor these into a base class for DRY
    type = serializers.SerializerMethodField()
    pk = serializers.ReadOnlyField()

    sources_ss = serializers.SlugRelatedField(
        source="sources",
        many=True,
        read_only=True,
        slug_field="display_name"
    )
    city_s = serializers.ReadOnlyField(source="city.name")
    country_s = serializers.ReadOnlyField(source="city.parent.name")
    name_s = serializers.ReadOnlyField(source="name")
    siglum_s = serializers.ReadOnlyField(source="siglum")

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()
