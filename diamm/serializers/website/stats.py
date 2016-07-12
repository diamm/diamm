import serpy
from diamm.serializers.serializers import ContextDictSerializer


class StatsSerializer(ContextDictSerializer):
    sources = serpy.IntField(
        attr='source'
    )
    sources_with_images = serpy.IntField(
        attr='source_with_images'
    )
    archives = serpy.IntField(
        attr='archive'
    )
    compositions = serpy.IntField(
        attr='composition'
    )
    people = serpy.IntField(
        attr='person'
    )
    composers = serpy.IntField(
        attr='composer'
    )
