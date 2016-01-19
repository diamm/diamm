from rest_framework import serializers
from diamm.models.data.composition import Composition
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.item import Item


class CompositionSourceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name='source-detail',
                                              source='source.id',
                                              read_only=True)

    display_name = serializers.ReadOnlyField(source='source.display_name')
    class Meta:
        model = Item
        fields = ('url', 'display_name')


class CompositionComposerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name="person-detail",
                                              source="composer.id",
                                              read_only=True)
    full_name = serializers.ReadOnlyField(source="composer.full_name")

    class Meta:
        model = CompositionComposer
        fields = ('url', 'full_name', 'uncertain', 'notes')


class CompositionListSerializer(serializers.HyperlinkedModelSerializer):
    composers = CompositionComposerSerializer(many=True)
    class Meta:
        model = Composition
        fields = ('url', 'name', 'composers')


class CompositionDetailSerializer(serializers.HyperlinkedModelSerializer):
    composers = CompositionComposerSerializer(many=True)
    sources = CompositionSourceSerializer(many=True)
    class Meta:
        model = Composition
        fields = ('url', 'name', 'composers', 'sources')
