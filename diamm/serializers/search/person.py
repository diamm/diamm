import serpy
from diamm.models.data.person_note import PersonNote
from diamm.serializers.serializers import ContextSerializer


class PersonSearchSerializer(ContextSerializer):
    pk = serpy.IntField()
    type = serpy.MethodField()
    name_s = serpy.StrField(
        attr="full_name"
    )
    # Copy the full name to a sorting field
    display_name_ans = serpy.StrField(
        attr="full_name"
    )
    last_name_s = serpy.StrField(
        attr="last_name"
    )
    first_name_s = serpy.StrField(
        attr="first_name",
        required=False
    )
    title_s = serpy.StrField(
        attr="title",
        required=False
    )
    role_ss = serpy.MethodField()
    start_date_i = serpy.IntField(
        attr="earliest_year",
        required=False
    )
    end_date_i = serpy.IntField(
        attr="latest_year",
        required=False
    )
    variant_names_ss = serpy.MethodField()
    genres_ss = serpy.MethodField()
    compositions_ss = serpy.MethodField()

    def get_role_ss(self, obj):
        return [role.role for role in obj.roles.all()]

    def get_variant_names_ss(self, obj):
        vnames = []
        for n in obj.notes.filter(type=PersonNote.VARIANT_NAME_NOTE):
            vnames = vnames + [o.strip() for o in n.note.split(";")]
        return vnames

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_genres_ss(self, obj):
        return list(obj.compositions.filter(composition__genres__isnull=False).values_list('composition__genres__name', flat=True).distinct())

    def get_compositions_ss(self, obj):
        return list(obj.compositions.all().values_list('composition__title', flat=True).distinct())

