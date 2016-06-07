from rest_framework import serializers
from diamm.models.data.composition import Composition
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.item import Item


class CompositionSourceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name='source-detail',
                                              source='source.id',
                                              read_only=True)
    has_images = serializers.SerializerMethodField()

    display_name = serializers.ReadOnlyField(source='source.display_name')
    public_images = serializers.ReadOnlyField(source='source.public_images')

    class Meta:
        model = Item
        fields = ('url', 'display_name', 'public_images', 'has_images')

    def get_has_images(self,obj):
        if obj.pages.count() > 0:
            return True
        return False


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
        fields = ('url', 'title', 'composers')


class CompositionDetailSerializer(serializers.HyperlinkedModelSerializer):
    composers = CompositionComposerSerializer(many=True)
    sources = CompositionSourceSerializer(many=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = Composition
        fields = ('url', 'title', 'composers', 'sources', 'pk', 'type')

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()

