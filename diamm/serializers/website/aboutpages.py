import serpy
from diamm.serializers.serializers import ContextSerializer


class AboutPagesSerializer(ContextSerializer):
    url = serpy.StrField()
    content = serpy.StrField()
    title = serpy.StrField()




