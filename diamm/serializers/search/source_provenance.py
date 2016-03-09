import serpy
from diamm.models.data.person import Person
from diamm.models.data.organization import Organization


class SourceProvenanceSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    source_i = serpy.IntField(
        attr="source.pk"
    )

    city_s = serpy.MethodField()
    country_s = serpy.MethodField()
    region_s = serpy.MethodField()
    protectorate_s = serpy.MethodField()

    uncertain_b = serpy.BoolField(
        attr="uncertain",
        required=False
    )
    earliest_year_i = serpy.IntField(
        attr="earliest_year",
        required=False
    )
    latest_year_i = serpy.IntField(
        attr="latest_year",
        required=False
    )
    entity_type_s = serpy.MethodField()
    entity_pk_i = serpy.MethodField()

    entity_s = serpy.MethodField()

    def get_city_s(self, obj):
        if obj.city:
            return obj.city.name
        return None

    def get_country_s(self, obj):
        if obj.country:
            return obj.country.name
        return None

    def get_region_s(self, obj):
        if obj.region:
            return obj.region.name
        return None

    def get_protectorate_s(self, obj):
        if obj.protectorate:
            return obj.protectorate.name
        return None

    def get_entity_type_s(self, obj):
        if isinstance(obj.entity, Organization):
            return "organization"
        elif isinstance(obj.entity, Person):
            return "person"
        else:
            return None

    def get_entity_s(self, obj):
        objtype = ""
        name = ""

        if isinstance(obj.entity, Organization):
            objtype = "organization"
            name = obj.entity.name
        elif isinstance(obj.entity, Person):
            objtype = "person"
            name = obj.entity.full_name
        else:
            return None

        return "{0}|{1}|{2}".format(name, obj.entity.pk, objtype)

    def get_entity_pk_i(self, obj):
        if obj.entity:
            return obj.entity.pk
        return None

    def get_type(self, obj):
        return obj.__class__.__name__.lower()
