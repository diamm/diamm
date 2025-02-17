
import serpy


class SetSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    cluster_shelfmark_s = serpy.StrField(attr="cluster_shelfmark")

    # allow sorting by alpha-numeric shelfmark.
    cluster_shelfmark_ans = serpy.StrField(attr="cluster_shelfmark")

    display_name_ans = serpy.StrField(attr="cluster_shelfmark")

    sources_ii = serpy.MethodField()
    set_type_s = serpy.StrField(attr="set_type")
    archives_ss = serpy.MethodField()
    archives_cities_ss = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    # add archive names to sets so that people can search for "partbooks oxford" or "trinity college partbooks"
    def get_archives_ss(self, obj) -> list | None:
        if obj.sources.exists():
            archives_set = set(
                obj.sources.all()
                .select_related("archive__city")
                .distinct()
                .values_list("archive__name", "archive__city__name")
            )
            return [", ".join(entry) for entry in archives_set]
        return None

    # add archive cities so that people can search for e.g., 'london partbooks' or 'cambridge partbooks'
    def get_archives_cities_ss(self, obj) -> list | None:
        if obj.sources.exists():
            return list(
                set(
                    obj.sources.all()
                    .select_related("archive__city")
                    .distinct()
                    .values_list("archive__city__name", flat=True)
                )
            )
        return None

    def get_sources_ii(self, obj) -> list:
        if obj.sources.exists():
            return list(obj.sources.values_list("pk", flat=True))
        return []
