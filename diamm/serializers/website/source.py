from rest_framework import serializers
from diamm.models.data.source import Source
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.archive import Archive
from diamm.models.data.item import Item
from diamm.models.data.item_note import ItemNote
from diamm.models.data.composition import Composition
from diamm.models.data.person import Person
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.geographic_area import GeographicArea


class CompositionComposerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name="person-detail",
                                              source="composer.id",
                                              read_only=True)
    full_name = serializers.ReadOnlyField(source="composer.full_name")

    class Meta:
        model = CompositionComposer
        fields = ('url', 'full_name', 'uncertain', 'notes')


class SourceItemCompositionSerializer(serializers.HyperlinkedModelSerializer):
    composers = CompositionComposerSerializer(many=True)

    class Meta:
        model = Composition
        fields = ('url', 'name', 'composers')


class SourceItemNoteSerializer(serializers.ModelSerializer):
    note_type = serializers.ReadOnlyField()

    class Meta:
        model = ItemNote
        fields = ('note_type', 'type', 'note')


class AggregateComposerSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Person
        fields = ('full_name',)


class SourceItemSerializer(serializers.ModelSerializer):
    composition = SourceItemCompositionSerializer()
    item_type = serializers.ReadOnlyField()
    notes = SourceItemNoteSerializer(
        many=True
    )
    aggregate_composer = AggregateComposerSerializer()

    class Meta:
        model = Item
        fields = ('composition',
                  'item_type',
                  'folio_start',
                  'folio_end',
                  'notes',
                  'aggregate_composer')


class SourceNoteSerializer(serializers.ModelSerializer):
    note_type = serializers.ReadOnlyField()

    class Meta:
        model = SourceNote
        fields = ('note_type', 'note', 'type')


class SourceIdentifierSerializer(serializers.ModelSerializer):
    identifier_type = serializers.ReadOnlyField()

    class Meta:
        model = SourceIdentifier
        fields = ('identifier', 'type', 'identifier_type', 'note')


class CityArchiveSourceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="city-detail",
    )
    class Meta:
        model = GeographicArea
        fields = ('url', 'name')


class ArchiveSourceSerializer(serializers.HyperlinkedModelSerializer):
    city = CityArchiveSourceSerializer()

    class Meta:
        model = Archive
        fields = ('url', 'name', 'city')


class SourceListSerializer(serializers.HyperlinkedModelSerializer):
    shelfmark = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = Source
        fields = ('url', 'name', 'display_name', 'shelfmark')


class SourceDetailSerializer(serializers.HyperlinkedModelSerializer):
    shelfmark = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    notes = SourceNoteSerializer(
        SourceNote.objects.exclude(type=SourceNote.PRIVATE_NOTE),
        many=True
    )
    identifiers = SourceIdentifierSerializer(
        many=True
    )

    surface_type = serializers.ReadOnlyField()
    archive = ArchiveSourceSerializer()
    inventory = SourceItemSerializer(many=True)
    notes = SourceNoteSerializer(
        source="public_notes",
        many=True
    )

    class Meta:
        model = Source
        fields = ('url',
                  'name',
                  'archive',
                  'display_name',
                  'shelfmark',
                  'notes',
                  'identifiers',
                  'surface',
                  'surface_type',
                  'inventory')
