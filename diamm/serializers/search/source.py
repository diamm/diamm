import uuid
from django.core.urlresolvers import reverse
from rest_framework import serializers
from diamm.models.data.source import Source


class SourceSearchSerializer(serializers.ModelSerializer):
    class Meta:
        search_type = "source"
        search_view = "source-detail"
        model = Source
        fields = ("id",
                  "url",
                  "type",
                  "pk",
                  'name_s',
                  'archive_s',
                  'surface_type_s',
                  'identifiers_ss',
                  'notes_ss',
                  'copyists_ss',
                  'start_date_i',
                  'end_date_i',
                  'composers_ss',
                  'compositions_ss')

    # TODO: Find some way to refactor these into a base class for DRY
    id = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    pk = serializers.ReadOnlyField()

    name_s = serializers.ReadOnlyField(source="name")
    archive_s = serializers.ReadOnlyField(source="archive.name")
    identifiers_ss = serializers.SlugRelatedField(
        source="identifiers",
        many=True,
        read_only=True,
        slug_field="identifier"
    )
    copyists_ss = serializers.SlugRelatedField(
        source="copyists",
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    notes_ss = serializers.SlugRelatedField(
        source="public_notes",
        many=True,
        read_only=True,
        slug_field="note"
    )
    start_date_i = serializers.IntegerField(source="start_date")
    end_date_i = serializers.IntegerField(source="end_date")
    surface_type_s = serializers.ReadOnlyField(source="surface_type")
    composers_ss = serializers.ListField(
        source="composers",
        child=serializers.CharField()
    )
    compositions_ss = serializers.ListField(
        source="compositions",
        child = serializers.CharField()
    )

    def get_type(self, obj):
        return self.Meta.search_type

    def get_id(self, obj):
        return "{0}".format(uuid.uuid4())

    def get_url(self, obj):
        return "{0}".format(
            reverse(self.Meta.search_view, kwargs={'pk': obj.pk})
        )

