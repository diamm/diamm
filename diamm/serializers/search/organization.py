import serpy


class OrganizationSearchSerializer(serpy.Serializer):

    type = serpy.MethodField()
    pk = serpy.IntField()

    location_s = serpy.StrField(
        attr="location.name",
        required=False
    )
    name_s = serpy.StrField(
        attr="name",
    )
    organization_type_s = serpy.StrField(
        attr="type",
        required=False
    )

    def get_type(self, obj):
        return obj.__class__.__name__.lower()
