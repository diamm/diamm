import serpy


class CorrectionSerializer(serpy.Serializer):
    summary = serpy.StrField()
    contributor = serpy.StrField(attr="contributor.full_name", required=False)
    credit = serpy.StrField()
    updated = serpy.StrField()
