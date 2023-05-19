from rest_framework import generics

from diamm.models.data.organization import Organization
from diamm.serializers.website.organization import OrganizationDetailSerializer


class OrganizationDetail(generics.RetrieveAPIView):
    template_name = "website/organization/organization_detail.jinja2"
    serializer_class = OrganizationDetailSerializer

    def get_queryset(self):
        queryset = Organization.objects.all().select_related('type', 'location__parent')
        return queryset
