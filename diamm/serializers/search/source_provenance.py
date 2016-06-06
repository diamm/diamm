import serpy
from diamm.models.data.person import Person
from diamm.models.data.organization import Organization


class SourceProvenanceSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

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

    city_s = serpy.MethodField()
    country_s = serpy.MethodField()
    region_s = serpy.MethodField()
    protectorate_s = serpy.MethodField()

    country_uncertain_b = serpy.BoolField(
        attr="country_uncertain",
        required=False
    )
    city_uncertain_b = serpy.BoolField(
        attr="city_uncertain",
        required=False
    )
    entity_uncertain_b = serpy.BoolField(
        attr="entity_uncertain",
        required=False
    )
    region_uncertain_b = serpy.BoolField(
        attr="region_uncertain",
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
        if isinstance(obj.entity, Organization):
            return obj.entity.name
        elif isinstance(obj.entity, Person):
            return obj.entity.full_name
        else:
            return None

    def get_entity_pk_i(self, obj):
        if obj.entity:
            return obj.entity.pk
        return None

    def get_type(self, obj):
        return obj.__class__.__name__.lower()
