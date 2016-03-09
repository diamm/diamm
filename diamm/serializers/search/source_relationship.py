import serpy
from diamm.models.data.organization import Organization
from diamm.models.data.person import Person


class SourceRelationshipSerializer(serpy.Serializer):
    pk = serpy.IntField()
    type = serpy.MethodField()

    source_i = serpy.IntField(
        attr="source.pk"
    )

    uncertain_b = serpy.BoolField(
        attr="uncertain"
    )

    relationship_type_s = serpy.MethodField()
    related_entity_type_s = serpy.MethodField()
    related_entity_pk_i = serpy.IntField(
        attr='related_entity.pk'
    )
    related_entity_s = serpy.MethodField()

    def get_related_entity_type_s(self, obj):
        if isinstance(obj.related_entity, Organization):
            return 'organization'
        elif isinstance(obj.related_entity, Person):
            return 'person'
        else:
            return None

    def get_related_entity_s(self, obj):
        objtype = ""
        name = ""

        if isinstance(obj.related_entity, Organization):
            objtype = "organization"
            name = obj.related_entity.name
        elif isinstance(obj.related_entity, Person):
            objtype = "person"
            name = obj.related_entity.full_name
        else:
            return None

        return "{0}|{1}|{2}".format(name, obj.related_entity.pk, objtype)

    def get_relationship_type_s(self, obj):
        if obj.relationship_type:
            return obj.relationship_type.name
        return None

    def get_type(self, obj):
        return obj.__class__.__name__.lower()
