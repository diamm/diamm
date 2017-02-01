from rest_framework import generics


class RegionDetail(generics.RetrieveAPIView):
    template_name = "website/"
