import serpy
from diamm.serializers.serializers import ContextSerializer


class ArchiveSearchSerializer(ContextSerializer):
    pk = serpy.IntField()
    type = serpy.MethodField()
    sources_ss = serpy.MethodField()
    city_s = serpy.StrField(attr="city.name")
    name_s = serpy.StrField(attr="name")
    country_s = serpy.StrField(attr="city.parent.name")
    siglum_s = serpy.StrField(attr="siglum")

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_sources_ss(self, obj):
        return [source.display_name for source in obj.sources.all()]
