import serpy

from diamm.serializers.serializers import ContextDictSerializer

class StatsSerializer(ContextDictSerializer):
    source = serpy.IntField(label='sources')
    source_with_images = serpy.IntField(label='sources_with_images')
    archive = serpy.IntField(label='archives')
    composition = serpy.IntField(label='compositions')
    person = serpy.IntField(label='people')
    composer = serpy.IntField(label='composers')
