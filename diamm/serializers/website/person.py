from rest_framework import serializers
from diamm.models.data.person import Person
from diamm.models.data.person_note import PersonNote
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.source import Source
from diamm.models.data.source_person import SourcePerson
from diamm.models.data.source_relationship_type import SourceRelationshipType
from diamm.models.data.archive import Archive


class PersonSourceRelationshipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceRelationshipType
        fields = ('name',)


class PersonSourceRelationshipSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name="source-detail",
                                              source="source.id",
                                              read_only=True)
    display_name = serializers.ReadOnlyField(source="source.display_name")
    archive = serializers.ReadOnlyField(source="source.archive.name")
    relationship_type = PersonSourceRelationshipTypeSerializer()

    class Meta:
        model = SourcePerson
        fields = ('url', 'archive', 'display_name', 'relationship_type')


class PersonSourceArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = ('url', 'name', 'city')


class PersonSourceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(source="source.id",
                                              view_name="source-detail",
                                              read_only=True)
    display_name = serializers.ReadOnlyField(source="source.display_name")
    archive = PersonSourceArchiveSerializer(source="source.archive")

    class Meta:
        model = Source
        fields = ('url', 'display_name', 'archive')


class PersonCompositionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name="composition-detail",
                                              source="composition.id",
                                              read_only=True)
    name = serializers.ReadOnlyField(source="composition.name")
    sources = PersonSourceSerializer(source="composition.sources", many=True)
    uncertain = serializers.ReadOnlyField()

    class Meta:
        model = CompositionComposer
        fields = ('url', 'name', 'sources', 'uncertain')


class PersonNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonNote
        fields = ('note', 'type')


class PersonListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person


class PersonDetailSerializer(serializers.HyperlinkedModelSerializer):
    compositions = PersonCompositionSerializer(many=True)
    full_name = serializers.ReadOnlyField()
    source_relationships = PersonSourceRelationshipSerializer(many=True)
    notes = PersonNoteSerializer(
        source="public_notes",
        many=True
    )

    class Meta:
        model = Person
        fields = ('url',
                  'full_name',
                  'compositions',
                  'source_relationships',
                  'notes')
