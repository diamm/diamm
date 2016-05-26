from rest_framework import generics
from diamm.models.site.contribution import Contribution
from diamm.serializers.website.contribution import ContributionSerializer


class ContributionList(generics.ListAPIView):
    template_name = "contribution_list.jinja2"
    serializer_class = ContributionSerializer
    queryset = Contribution.objects.all()


class ContributionDetail(generics.RetrieveAPIView):
    template_name = "contribution_detail.jinja2"
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
