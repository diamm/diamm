import serpy
from diamm.models.data.person import Person
from diamm.models.data.organization import Organization


class SourceCopyistSearchSerializer(serpy.Serializer):
    pk = serpy.IntField()
    type = serpy.MethodField()

    # The type of copyist: Illuminator, music, etc.
    type_s = serpy.StrField(
        attr="copyist_type",
        required=False
    )
    source_i = serpy.IntField(
            attr="source.pk"
    )
    source_s = serpy.StrField(
            attr="source.display_name"
    )
    # Sort by the source name *with the archive sigla*
    source_ans = serpy.StrField(
            attr="source.display_name"
    )
    copyist_type_s = serpy.MethodField()
    copyist_pk_i = serpy.MethodField()
    copyist_s = serpy.MethodField()
    uncertain_b = serpy.BoolField(
        attr="uncertain"
    )

    def get_copyist_type_s(self, obj):
        if isinstance(obj.copyist, Organization):
            return "organization"
        elif isinstance(obj.copyist, Person):
            return "person"
        else:
            return None

    def get_copyist_s(self, obj):
        if isinstance(obj.copyist, Organization):
            return obj.copyist.name
        elif isinstance(obj.copyist, Person):
            return obj.copyist.full_name
        else:
            return None

    def get_copyist_pk_i(self, obj):
        if obj.copyist:
            return obj.copyist.pk
        return None



    def get_type(self, obj):
        return obj.__class__.__name__.lower()
