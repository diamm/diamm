import serpy
from diamm.serializers.serializers import ContextSerializer


class ProvenanceSerializer(ContextSerializer):
    name = serpy.StrField()
