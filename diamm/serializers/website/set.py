import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class SetSourceSerializer(ContextSerializer):
    url = serpy.MethodField()
    shelfmark = serpy.StrField()
    display_name = serpy.StrField(
        required=False
    )

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])


class SetDetailSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    type = serpy.StrField(
        attr='set_type'
    )
    cluster_shelfmark = serpy.StrField()
    sources = serpy.MethodField()

    def get_url(self, obj):
        return reverse('set-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_sources(self, obj):
        if obj.sources:
            return [SetSourceSerializer(o, context={'request': self.context['request']}).data
                    for o in obj.sources.all()]
        else:
            return None
