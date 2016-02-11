from rest_framework import serializers
from diamm.models.data.source import Source


class SourceSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ("type",
                  "pk",
                  'shelfmark_s',
                  'shelfmark_ans',
                  'name_s',
                  'archive_s',
                  'surface_type_s',
                  'source_type_s',
                  'date_statement_s',
                  'measurements_s',
                  'identifiers_ss',
                  'notes_txt',
                  'start_date_i',
                  'end_date_i',
                  'composers_ss')

    # TODO: Find some way to refactor these into a base class for DRY
    type = serializers.SerializerMethodField()
    pk = serializers.ReadOnlyField()

    shelfmark_s = serializers.ReadOnlyField(source='shelfmark')
    # Alphanumeric sort field for shelfmarks.
    shelfmark_ans = serializers.ReadOnlyField(source="shelfmark")
    name_s = serializers.ReadOnlyField(source="display_name")
    archive_s = serializers.ReadOnlyField(source="archive.name")
    measurements_s = serializers.ReadOnlyField(source='measurements')
    identifiers_ss = serializers.SlugRelatedField(
        source="identifiers",
        many=True,
        read_only=True,
        slug_field="identifier"
    )

    notes_txt = serializers.SlugRelatedField(
        source="public_notes",
        many=True,
        read_only=True,
        slug_field="note"
    )
    start_date_i = serializers.IntegerField(source="start_date")
    end_date_i = serializers.IntegerField(source="end_date")
    date_statement_s = serializers.SerializerMethodField()
    surface_type_s = serializers.ReadOnlyField(source="surface_type")
    source_type_s = serializers.ReadOnlyField(source="type")
    composers_ss = serializers.ListField(
        source="composers",
        child=serializers.CharField()
    )

    def get_date_statement_s(self, obj):
        return "; ".join([n.note for n in obj.date_notes.all()])

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()
