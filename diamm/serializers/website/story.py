import serpy
from rest_framework.reverse import reverse
from diamm.serializers.website.tag import TagSerializer
from diamm.serializers.serializers import ContextSerializer

class StorySerializer(ContextSerializer):
    title = serpy.StrField()
    body = serpy.StrField()
    tags = serpy.MethodField()
    created = serpy.StrField()
    updated = serpy.StrField()
    url = serpy.MethodField()

    def get_tags(self, obj):
        return TagSerializer(
            obj.tags.all(),
            many=True,
            context={'request': self.context['request']}).data

    def get_url(self, obj):
        return reverse("tag-detail",
                kwargs={"pk": obj.pk},
                request=self.context['request'])
