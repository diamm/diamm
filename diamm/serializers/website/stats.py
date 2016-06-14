import serpy

from diamm.serializers.serializers import ContextDictSerializer

class StatsSerializer(ContextDictSerializer):
    source = serpy.IntField()
    source_with_images = serpy.IntField()
    archive = serpy.IntField()
    composition = serpy.IntField()
    person = serpy.IntField()
