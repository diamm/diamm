import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class RegionDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    pk = serpy.IntField()
    name = serpy.StrField()
    # provenance_relationships = serpy.MethodField()
    # organizations = serpy.MethodField()

    def get_url(self, obj):
        return reverse("city-detail", kwargs={"pk": obj.id}, request=self.context['request'])
