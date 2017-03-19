import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class SetSourceSerializer(ContextSerializer):
    url = serpy.MethodField()
    shelfmark = serpy.StrField()
    public_images = serpy.BoolField()
    has_images = serpy.MethodField()
    display_name = serpy.StrField(
        required=False
    )
    archive_name = serpy.StrField(
        attr="archive.name"
    )

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_has_images(self, obj):
        if obj.pages.count() > 0:
            return True
        return False


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
            return SetSourceSerializer(obj.sources.all(),
                                       many=True,
                                       context={'request': self.context['request']}).data
        else:
            return None
