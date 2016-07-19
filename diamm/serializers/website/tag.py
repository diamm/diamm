import serpy
from diamm.serializers.serializers import ContextSerializer

class TagSerializer(ContextSerializer):
    tag = serpy.StrField()
