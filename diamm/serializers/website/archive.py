from rest_framework import serializers
from diamm.models.data.archive import Archive
from diamm.models.data.archive_note import ArchiveNote
from diamm.models.data.source import Source
from diamm.models.data.geographic_area import GeographicArea


class CityArchiveSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="city-detail")

    class Meta:
        model = GeographicArea
        fields = ('url', 'name')


class SourceArchiveSerializer(serializers.HyperlinkedModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = Source
        fields = ('url', 'display_name')


class ArchiveNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchiveNote
        fields = ('type', 'note')


class ArchiveListSerializer(serializers.HyperlinkedModelSerializer):
    city = CityArchiveSerializer()

    class Meta:
        model = Archive
        fields = ('url', 'name', 'city')


class ArchiveDetailSerializer(serializers.HyperlinkedModelSerializer):
    city = CityArchiveSerializer()
    sources = SourceArchiveSerializer(many=True)
    # notes = ArchiveNoteSerializer(
    #     source="public_notes",
    #     many=True
    # )

    class Meta:
        model = Archive
        fields = ('url',
                  'name',
                  'city',
                  'sources',
                  'siglum',
                  'website')
