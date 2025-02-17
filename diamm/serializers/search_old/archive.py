
import serpy

from diamm.serializers.serializers import ContextSerializer


class ArchiveSearchSerializer(ContextSerializer):
    pk = serpy.IntField()
    type = serpy.MethodField()
    sources_ss = serpy.MethodField()
    city_s = serpy.StrField(attr="city.name")
    city_variants_ss = serpy.MethodField()
    name_s = serpy.StrField(attr="name")
    display_name_ans = serpy.StrField(attr="name")
    country_s = serpy.StrField(attr="city.parent.name", required=False)
    siglum_s = serpy.StrField(attr="siglum")
    former_sigla_ss = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_city_variants_ss(self, obj) -> list:
        if obj.city.variant_names:
            return [variant.strip() for variant in obj.city.variant_names.split(",")]
        return []

    def get_sources_ss(self, obj) -> list:
        return [source.display_name for source in obj.sources.all()]

    def get_former_sigla_ss(self, obj) -> list | None:
        if obj.former_sigla:
            return obj.former_sigla.split(",")
        return None
