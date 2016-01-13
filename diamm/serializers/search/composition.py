import uuid
from django.core.urlresolvers import reverse
from rest_framework import serializers
from diamm.models.data.composition import Composition


class CompositionSearchSerializer(serializers.ModelSerializer):
    class Meta:
        search_type = "composition"
        search_view = "composition-detail"
        model = Composition
        fields = (
            "id",
            "url",
            "type",
            "pk",
            "name_s",
            "genres_ss",
            "composers_ss"
        )

    # TODO: Find some way to refactor these into a base class for DRY
    id = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    pk = serializers.ReadOnlyField()

    name_s = serializers.CharField(source="name")
    genres_ss = serializers.SlugRelatedField(
        source="genres",
        many=True,
        read_only=True,
        slug_field="name"
    )
    composers_ss = serializers.SerializerMethodField()

    def get_composers_ss(self, obj):
        return [o.composer.full_name for o in obj.composers.all()]

    def get_type(self, obj):
        return self.Meta.search_type

    def get_id(self, obj):
        return "{0}".format(uuid.uuid4())

    def get_url(self, obj):
        return "{0}".format(
            reverse(self.Meta.search_view, kwargs={'pk': obj.pk})
        )

