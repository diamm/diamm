import serpy


class CompositionSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    name_s = serpy.StrField(
        attr="name"
    )
    genres_ss = serpy.MethodField()
    composers_ss = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_genres_ss(self, obj):
        if obj.genres:
            return list(obj.genres.all().values_list('name', flat=True))
        return []

    def get_composers_ss(self, obj):
        if obj.composers:
            return [o.composer.full_name for o in obj.composers.all()]
        return []
