import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer, ContextDictSerializer
from diamm.models.data.geographic_area import GeographicArea


class OrganizationContributionSerializer(ContextSerializer):
    contributor = serpy.StrField(
        attr="contributor.username"
    )
    summary = serpy.StrField()
    updated = serpy.StrField()


class OrganizationLocationSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField(
        attr='name'
    )

    def get_url(self, obj):
        view_type = None
        if obj.type == GeographicArea.CITY:
            view_type = "city-detail"
        elif obj.type == GeographicArea.COUNTRY:
            view_type = "country-detail"

        if view_type:
            return reverse(view_type,
                           kwargs={"pk": obj.pk},
                           request=self.context['request'])
        else:
            return None


class OrganizationSourceProvenanceSerializer(ContextDictSerializer):
    url = serpy.MethodField()

    source = serpy.StrField(
        attr="source_s"
    )

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj['source_i']},
                       request=self.context['request'])


class OrganizationSourceCopyistSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    copyist_type = serpy.StrField(
        attr="type_s"
    )
    uncertain = serpy.BoolField(
        attr="uncertain_b"
    )
    source = serpy.StrField(
        attr="source_s"
    )

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj['source_i']},
                       request=self.context['request'])


class OrganizationSourceRelationshipSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    relationship = serpy.StrField(
        attr="relationship_type_s"
    )
    uncertain = serpy.BoolField(
        attr="uncertain_b"
    )
    source = serpy.StrField(
        attr="source_s"
    )

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj['source_i']},
                       request=self.context['request'])


class OrganizationDetailSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    name = serpy.StrField()
    organization_type = serpy.StrField(
        attr="type.name"
    )
    type = serpy.MethodField()
    related_sources = serpy.MethodField()
    copied_sources = serpy.MethodField()
    source_provenance = serpy.MethodField()
    location = serpy.MethodField()
    contributors = serpy.MethodField()

    def get_url(self, obj):
        return reverse('organization-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_location(self, obj):
        if obj.location:
            return OrganizationLocationSerializer(obj.location, context={"request": self.context["request"]}).data
        return None

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_related_sources(self, obj):
        return OrganizationSourceRelationshipSerializer(obj.solr_relationships,
                                                         many=True,
                                                         context={"request": self.context["request"]}).data

    def get_copied_sources(self, obj):
        return OrganizationSourceCopyistSerializer(obj.solr_copyist,
                                                   many=True,
                                                   context={"request": self.context['request']}).data

    def get_source_provenance(self, obj):
        return OrganizationSourceProvenanceSerializer(obj.solr_provenance,
                                                      many=True,
                                                      context={"request": self.context['request']}).data

    def get_contributors(self, obj):
        if obj.contributions.count() > 0:
            return OrganizationContributionSerializer(obj.contributions.filter(completed=True),
                                                      context={"request": self.context['request']},
                                                      many=True).data
        return []
