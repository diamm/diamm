import serpy


class BibliographySearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    title_s = serpy.StrField(
        attr="title"
    )
    year_s = serpy.StrField(
        attr="year"
    )
    type_s = serpy.StrField(
        attr="type.name"
    )
    abbreviation_s = serpy.StrField(
        attr="abbreviation"
    )


    def get_type(self, obj):
        return obj.__class__.__name__.lower()
