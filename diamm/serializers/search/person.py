import uuid
from django.core.urlresolvers import reverse
from rest_framework import serializers
from diamm.models.data.person import Person
from diamm.models.data.person_note import PersonNote


class PersonSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id",
                  "type",
                  "pk",
                  "full_name_s",
                  "last_name_s",
                  "first_name_s",
                  "role_ss",
                  "start_date_i",
                  "end_date_i",
                  "variant_names_ss")

    # TODO: Find some way to refactor these into a base class for DRY
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    pk = serializers.ReadOnlyField()

    full_name_s = serializers.ReadOnlyField(source="full_name")
    last_name_s = serializers.ReadOnlyField(source="last_name")
    first_name_s = serializers.ReadOnlyField(source="first_name")
    role_ss = serializers.SlugRelatedField(
        source="roles",
        many=True,
        read_only=True,
        slug_field='name'
    )
    start_date_i = serializers.IntegerField(source="earliest_year")
    end_date_i = serializers.IntegerField(source="latest_year")
    variant_names_ss = serializers.SerializerMethodField()

    def get_variant_names_ss(self, obj):
        vnames = []
        for n in obj.notes.filter(type=PersonNote.VARIANT_NAME_NOTE):
            vnames = vnames + [o.strip() for o in n.note.split(";")]
        return vnames

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()

    def get_id(self, obj):
        return "{0}".format(uuid.uuid4())

