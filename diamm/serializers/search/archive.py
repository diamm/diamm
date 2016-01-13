import uuid
from django.core.urlresolvers import reverse
from rest_framework import serializers
from diamm.models.data.archive import Archive


class ArchiveSearchSerializer(serializers.ModelSerializer):
    class Meta:
        search_type = "archive"
        search_view = "archive-detail"
        model = Archive
        fields = ("id",
                  "url",
                  "type",
                  "pk",
                  "sources_ss",
                  "city_s",
                  "name_s",
                  "country_s")

    # TODO: Find some way to refactor these into a base class for DRY
    id = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    pk = serializers.ReadOnlyField()

    sources_ss = serializers.SlugRelatedField(
        source="sources",
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    city_s = serializers.ReadOnlyField(source="city.name")
    country_s = serializers.ReadOnlyField(source="city.parent.name")
    name_s = serializers.ReadOnlyField(source="name")

    def get_type(self, obj):
        return self.Meta.search_type

    def get_id(self, obj):
        return "{0}".format(uuid.uuid4())

    def get_url(self, obj):
        return "{0}".format(
            reverse(self.Meta.search_view, kwargs={'pk': obj.pk})
        )
