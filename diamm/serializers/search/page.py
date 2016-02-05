from rest_framework import serializers
from diamm.models.data.page import Page
from diamm.models.data.item import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('type',
                  'pk',
                  'numeration_s',
                  'source_i',
                  'legacy_id_s')

    def get_type(self, obj):
            return self.Meta.model.__name__.lower()


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('type',
                  'pk',
                  'numeration_s',
                  'source_i',
                  'legacy_id_s')

    # TODO: Find some way to refactor these into a base class for DRY
    type = serializers.SerializerMethodField()
    pk = serializers.ReadOnlyField()

    numeration_s = serializers.ReadOnlyField(source="numeration")
    source_i = serializers.ReadOnlyField(source="source.pk")
    legacy_id_s = serializers.ReadOnlyField(source="legacy_id")

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()
