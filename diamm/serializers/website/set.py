import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class SetDetailSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    type = serpy.StrField()

    def get_url(self, obj):
        return reverse('set-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])
