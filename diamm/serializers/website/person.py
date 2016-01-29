from rest_framework import serializers
from diamm.models.data.person import Person
from diamm.models.data.person_note import PersonNote
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.source import Source
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_relationship_type import SourceRelationshipType
from diamm.models.data.archive import Archive


class PersonSourceCopiedSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='source-detail',
                                               source='source.id',
                                               read_only=True)

    display_name = serializers.ReadOnlyField(source="source.display_name")
    type = serializers.ReadOnlyField()

    class Meta:
        model = SourceCopyist
        fields = ('url', 'display_name', 'type')


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
        model = SourceRelationship
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
        fields = ('note',)


class PersonListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ('url', 'full_name')


class PersonDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ('url',
                  'full_name',
                  'compositions',
                  'sources_related',
                  'sources_copied',
                  'biography',
                  'dates')

    compositions = PersonCompositionSerializer(many=True)
    full_name = serializers.ReadOnlyField()
    sources_related = PersonSourceRelationshipSerializer(many=True)
    sources_copied = PersonSourceCopiedSerializer(many=True)
    biography = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()

    def get_biography(self, obj):
        return PersonNoteSerializer(obj.notes.filter(type=PersonNote.BIOGRAPHY), many=True).data

    def get_dates(self, obj):
        return PersonNoteSerializer(obj.notes.filter(type=PersonNote.DATE_NOTE), many=True).data
