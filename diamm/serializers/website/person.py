from typing import Dict, List

import serpy
from rest_framework.reverse import reverse

from diamm.models.data.person_note import PersonNote
from diamm.serializers.serializers import ContextDictSerializer, ContextSerializer


class PersonRoleSerializer(ContextSerializer):
    earliest_year = serpy.StrField(
        required=False
    )
    earliest_year_approximate = serpy.BoolField()
    latest_year_approximate = serpy.BoolField()
    latest_year = serpy.StrField(
        required=False
    )
    role = serpy.StrField(
        attr="role_description"
    )
    note = serpy.StrField(
        required=False
    )


class PersonNoteSerializer(ContextSerializer):
    note = serpy.StrField()


class PersonContributionSerializer(ContextSerializer):
    contributor = serpy.StrField(
        attr="contributor.username"
    )
    summary = serpy.StrField()
    updated = serpy.StrField()


class PersonSourceCopyistSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    has_images = serpy.BoolField(
        attr="has_images_b",
        required=False
    )
    copyist_type = serpy.StrField(
        attr="type_s"
    )
    uncertain = serpy.BoolField(
        attr="uncertain_b"
    )
    source = serpy.StrField(
        attr="source_s"
    )
    public_images = serpy.BoolField(
        attr="source_public_images_b",
        required=False
    )

    def get_url(self, obj: Dict) -> str:
        return reverse("source-detail",
                       kwargs={"pk": obj['source_i']},
                       request=self.context['request'])


class PersonSourceRelationshipSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    has_images = serpy.BoolField(
        attr="has_images_b",
        required=False
    )
    relationship = serpy.StrField(
        attr="relationship_type_s"
    )
    uncertain = serpy.BoolField(
        attr="uncertain_b"
    )
    source = serpy.StrField(
        attr="source_s"
    )
    public_images = serpy.BoolField(
        attr="source_public_images_b",
        required=False
    )

    def get_url(self, obj: Dict) -> str:
        return reverse('source-detail',
                       kwargs={"pk": obj["source_i"]},
                       request=self.context['request'])


class PersonCompositionSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    title = serpy.StrField(
        attr='title_s'
    )
    uncertain = serpy.BoolField()  # injected in the person model lookup for solr_compositions
    sources = serpy.MethodField()

    def get_url(self, obj: Dict) -> str:
        return reverse('composition-detail',
                       kwargs={"pk": obj['pk']},
                       request=self.context['request'])

    def get_sources(self, obj: Dict) -> List:
        if 'sources_ss' not in obj:
            return []

        sources = []
        for entry in obj['sources_ssni']:
            pk, name = entry.split("|")
            d = {
                'url': reverse('source-detail',
                               kwargs={"pk": pk},
                               request=self.context['request']),
                'name': name
            }
            sources.append(d)

        return sources


class PersonIdentifierSerializer(ContextSerializer):
    url = serpy.StrField(attr="identifier_url")
    label = serpy.StrField(attr="identifier_label")
    identifier = serpy.StrField()


class PersonDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    pk = serpy.IntField()
    compositions = serpy.MethodField()
    related_sources = serpy.MethodField()
    copied_sources = serpy.MethodField()
    full_name = serpy.StrField()
    type = serpy.MethodField()
    earliest_year = serpy.IntField(
        required=False
    )
    earliest_year_approximate = serpy.BoolField(
        required=False
    )
    latest_year = serpy.IntField(
        required=False
    )
    latest_year_approximate = serpy.BoolField(
        required=False
    )
    # biography = serpy.MethodField()
    variant_names = serpy.MethodField()
    roles = serpy.MethodField()
    identifiers = serpy.MethodField(required=False)

    def get_url(self, obj) -> str:
        return reverse('person-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_compositions(self, obj) -> List:
        return PersonCompositionSerializer(obj.solr_compositions,
                                           context={'request': self.context['request']},
                                           many=True).data

    def get_related_sources(self, obj) -> List:
        return PersonSourceRelationshipSerializer(obj.solr_relationships,
                                                  context={"request": self.context['request']},
                                                  many=True).data

    def get_copied_sources(self, obj) -> List:
        return PersonSourceCopyistSerializer(obj.solr_copyist,
                                             context={"request": self.context['request']},
                                             many=True).data

    def get_type(self, obj) -> str:
        return obj.__class__.__name__.lower()

    # def get_biography(self, obj):
    #     return PersonNoteSerializer(obj.notes.filter(type=PersonNote.BIOGRAPHY, public=True), many=True).data

    def get_variant_names(self, obj) -> list:
        return list(obj.notes.filter(type=PersonNote.VARIANT_NAME_NOTE,
                                     public=True).values_list('note', flat=True))

    def get_roles(self, obj) -> List:
        return PersonRoleSerializer(obj.roles.all(), many=True).data

    def get_identifiers(self, obj) -> list:
        return PersonIdentifierSerializer(obj.identifiers.all(),
                                          many=True,
                                          context={"request": self.context['request']}).data
