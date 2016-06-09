import serpy
from diamm.models.data.organization import Organization
from diamm.models.data.person import Person


class SourceRelationshipSerializer(serpy.Serializer):
    pk = serpy.IntField()
    type = serpy.MethodField()
    has_images_b = serpy.MethodField()

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

    uncertain_b = serpy.BoolField(
        attr="uncertain"
    )
    public_images_b = serpy.BoolField(
        attr="source.public_images"
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
        if isinstance(obj.related_entity, Organization):
            return obj.related_entity.name
        elif isinstance(obj.related_entity, Person):
            return obj.related_entity.full_name
        else:
            return None

    def get_relationship_type_s(self, obj):
        if obj.relationship_type:
            return obj.relationship_type.name
        return None

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_has_images_b(self, obj):
        if obj.source.pages.count() > 0:
            return True
        return False