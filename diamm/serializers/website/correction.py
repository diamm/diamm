import ypres


class CorrectionSerializer(ypres.Serializer):
    summary = ypres.StrField()
    contributor = ypres.StrField(attr="contributor.full_name", required=False)
    credit = ypres.StrField()
    updated = ypres.StrField()
