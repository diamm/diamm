import serpy
from diamm.serializers.serializers import ContextSerializer
from rest_framework.reverse import reverse


class OrganizationListSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse('organization-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])


class OrganizationDetailSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    name = serpy.StrField()
    location = serpy.StrField()
    note = serpy.StrField(
        required=False
    )
    variant_names = serpy.StrField(
        required=False
    )

    #the name 'type' is needed for the content type but using organization.organization_type would be redundant
    organization_type = serpy.StrField(
        attr="type"
    )

    type = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_url(self, obj):
        return reverse('organization-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])