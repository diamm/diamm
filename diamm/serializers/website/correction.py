import serpy


class CorrectionSerializer(serpy.Serializer):
    note = serpy.StrField()
    contributor = serpy.StrField(
        attr="contributor.full_name"
    )
    created = serpy.StrField()
