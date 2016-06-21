import serpy


class OrganizationSearchSerializer(serpy.Serializer):

    type = serpy.MethodField()
    pk = serpy.IntField()

    location_s = serpy.MethodField()

    name_s = serpy.StrField(
        attr="name",
    )
    organization_type_s = serpy.StrField(
        attr="type",
        required=False
    )

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_location_s(self, obj):
        if obj.location:
            return obj.location.name
        else:
            return None
