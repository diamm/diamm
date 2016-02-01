from rest_framework import generics
from diamm.models.data.organization import Organization
from diamm.serializers.website.organization import OrganizationListSerializer, OrganizationDetailSerializer


class OrganizationList(generics.ListAPIView):
    template_name = "website/organization/organization_list.jinja2"
    queryset = Organization.objects.all()
    serializer_class = OrganizationListSerializer


class OrganizationDetail(generics.RetrieveAPIView):
    template_name = "website/organization/organization_detail.jinja2"
    queryset = Organization.objects.all()
    serializer_class = OrganizationDetailSerializer
