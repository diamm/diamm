import serpy


class SetSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    cluster_shelfmark_s = serpy.StrField(
        attr="cluster_shelfmark"
    )

    # allow sorting by alpha-numeric shelfmark.
    # cluster_shelfmark_ans = serpy.StrField(
    #     attr="cluster_shelfmark"
    # )

    sources_ii = serpy.MethodField()
    set_type_s = serpy.StrField(
        attr='set_type'
    )
    archives_ss = serpy.MethodField()
    archives_cities_ss = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    # add archive names to sets so that people can search for "partbooks oxford" or "trinity college partbooks"
    def get_archives_ss(self, obj):
        if obj.sources.count() > 0:
            return list(obj.sources.all().select_related('archive').distinct().values_list('archive__name', flat=True))
        else:
            return None

    # add archive cities so that people can search for e.g., 'london partbooks' or 'cambridge partbooks'
    def get_archives_cities_ss(self, obj):
        if obj.sources.count() > 0:
            return list(obj.sources.all().select_related('archive__city').distinct().values_list('archive__city__name', flat=True))
        else:
            return None

    def get_sources_ii(self, obj):
        if obj.sources.count() > 0:
            return list(obj.sources.all().values_list('pk', flat=True))
        else:
            return []
