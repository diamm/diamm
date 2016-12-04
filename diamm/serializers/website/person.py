import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextDictSerializer, ContextSerializer
from diamm.models.data.person_note import PersonNote


class PersonNoteSerializer(ContextSerializer):
    note = serpy.StrField()


class PersonContributionSerializer(ContextSerializer):
    contributor = serpy.StrField(
        attr="contributor.username"
    )
    summary = serpy.StrField()
    updated = serpy.StrField()


class PersonSourceCopyistSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    has_images = serpy.BoolField(
        attr="has_images_b",
        required=False
    )
    copyist_type = serpy.StrField(
        attr="type_s"
    )
    uncertain = serpy.BoolField(
        attr="uncertain_b"
    )
    source = serpy.StrField(
        attr="source_s"
    )
    public_images = serpy.BoolField(
        attr="public_images_b",
        required=False
    )

    def get_url(self, obj):
        return reverse("source-detail",
                       kwargs={"pk": obj['source_i']},
                       request=self.context['request'])


class PersonSourceRelationshipSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    has_images = serpy.BoolField(
        attr="has_images_b",
        required=False
    )
    relationship = serpy.StrField(
        attr="relationship_type_s"
    )
    uncertain = serpy.BoolField(
        attr="uncertain_b"
    )
    source = serpy.StrField(
        attr="source_s"
    )
    public_images = serpy.BoolField(
        attr="public_images_b",
        required=False
    )

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj["source_i"]},
                       request=self.context['request'])


class PersonCompositionSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    title = serpy.StrField(
        attr='title_s'
    )
    uncertain = serpy.BoolField()  # injected in the person model lookup for solr_compositions
    sources = serpy.MethodField()

    def get_url(self, obj):
        return reverse('composition-detail',
                       kwargs={"pk": obj['pk']},
                       request=self.context['request'])

    def get_sources(self, obj):
        if 'sources_ss' not in obj:
            return []
        sources = []
        for entry in obj['sources_ss']:
            pk, name = entry.split("|")
            d = {
                'url': reverse('source-detail',
                               kwargs={"pk": pk},
                               request=self.context['request']),
                'name': name
            }
            sources.append(d)

        return sources


class PersonDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    pk = serpy.IntField()
    compositions = serpy.MethodField()
    related_sources = serpy.MethodField()
    copied_sources = serpy.MethodField()
    full_name = serpy.StrField()
    type = serpy.MethodField()
    contributors = serpy.MethodField()
    earliest_year = serpy.IntField(
        required=False
    )
    earliest_year_approximate = serpy.BoolField(
        required=False
    )
    latest_year = serpy.IntField(
        required=False
    )
    latest_year_approximate = serpy.BoolField(
        required=False
    )
    biography = serpy.MethodField()
    variant_names = serpy.MethodField()

    def get_url(self, obj):
        return reverse('person-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_compositions(self, obj):
        return [PersonCompositionSerializer(o, context={'request': self.context['request']}).data for o in obj.solr_compositions]

    def get_related_sources(self, obj):
        return [PersonSourceRelationshipSerializer(o, context={"request": self.context['request']}).data for o in obj.solr_relationships]

    def get_copied_sources(self, obj):
        return [PersonSourceCopyistSerializer(o, context={"request": self.context['request']}).data for o in obj.solr_copyist]

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_contributors(self, obj):
        if obj.contributions.count() > 0:
            return PersonContributionSerializer(obj.contributions.filter(completed=True),
                                                context={"request": self.context['request']}, many=True).data

    def get_biography(self, obj):
        return PersonNoteSerializer(obj.notes.filter(type=PersonNote.BIOGRAPHY, public=True), many=True).data

    def get_variant_names(self, obj):
        return obj.notes.filter(type=PersonNote.VARIANT_NAME_NOTE, public=True).values_list('note', flat=True)

# from rest_framework import serializers
# from diamm.models.data.person import Person
# from diamm.models.data.person_note import PersonNote
# from diamm.models.data.composition_composer import CompositionComposer
# from diamm.models.data.source import Source
# from diamm.models.data.source_relationship import SourceRelationship
# from diamm.models.data.source_copyist import SourceCopyist
# from diamm.models.data.source_relationship_type import SourceRelationshipType
# from diamm.models.data.archive import Archive


# class PersonSourceCopiedSerializer(serializers.ModelSerializer):
#     url = serializers.HyperlinkedIdentityField(view_name='source-detail',
#                                                source='source.id',
#                                                read_only=True)
#
#     display_name = serializers.ReadOnlyField(source="source.display_name")
#     type = serializers.ReadOnlyField()
#
#     class Meta:
#         model = SourceCopyist
#         fields = ('url', 'display_name', 'type')
#
#
# class PersonSourceRelationshipTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SourceRelationshipType
#         fields = ('name',)
#
#
# class PersonSourceRelationshipSerializer(serializers.ModelSerializer):
#     url = serializers.HyperlinkedRelatedField(view_name="source-detail",
#                                               source="source.id",
#                                               read_only=True)
#     display_name = serializers.ReadOnlyField(source="source.display_name")
#     archive = serializers.ReadOnlyField(source="source.archive.name")
#     relationship_type = PersonSourceRelationshipTypeSerializer()
#
#     class Meta:
#         model = SourceRelationship
#         fields = ('url', 'archive', 'display_name', 'relationship_type')
#
#
# class PersonSourceArchiveSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Archive
#         fields = ('url', 'name', 'city')
#
#
# class PersonSourceSerializer(serializers.ModelSerializer):
#     url = serializers.HyperlinkedRelatedField(source="source.id",
#                                               view_name="source-detail",
#                                               read_only=True)
#     display_name = serializers.ReadOnlyField(source="source.display_name")
#     archive = PersonSourceArchiveSerializer(source="source.archive")
#
#     class Meta:
#         model = Source
#         fields = ('url', 'display_name', 'archive')
#
#
# class PersonCompositionSerializer(serializers.ModelSerializer):
#     url = serializers.HyperlinkedRelatedField(view_name="composition-detail",
#                                               source="composition.id",
#                                               read_only=True)
#     name = serializers.ReadOnlyField(source="composition.name")
#     sources = PersonSourceSerializer(source="composition.sources", many=True)
#     uncertain = serializers.ReadOnlyField()
#
#     class Meta:
#         model = CompositionComposer
#         fields = ('url', 'name', 'sources', 'uncertain')
#
#
# class PersonNoteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PersonNote
#         fields = ('note',)
#
#
# class PersonListSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Person
#         fields = ('url', 'full_name')
#
#
# class PersonDetailSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Person
#         fields = ('url',
#                   'full_name',
#                   'compositions',
#                   'sources_related',
#                   'sources_copied',
#                   'biography',
#                   'dates')
#
#     compositions = PersonCompositionSerializer(many=True)
#     full_name = serializers.ReadOnlyField()
#     sources_related = PersonSourceRelationshipSerializer(many=True)
#     sources_copied = PersonSourceCopiedSerializer(many=True)
#     biography = serializers.SerializerMethodField()
#     dates = serializers.SerializerMethodField()
#
#     def get_biography(self, obj):
#         return PersonNoteSerializer(obj.notes.filter(type=PersonNote.BIOGRAPHY), many=True).data
#
#     def get_dates(self, obj):
#         return PersonNoteSerializer(obj.notes.filter(type=PersonNote.DATE_NOTE), many=True).data
