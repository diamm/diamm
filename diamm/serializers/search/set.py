import serpy


class SetSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    cluster_shelfmark_s = serpy.StrField(
        attr="cluster_shelfmark"
    )
    sources_ii = serpy.MethodField()
    set_type_s = serpy.StrField(
        attr='set_type'
    )

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_sources_ii(self, obj):
        if obj.sources.count() > 0:
            return list(obj.sources.all().values_list('pk', flat=True))
        else:
            return []
