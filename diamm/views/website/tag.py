from rest_framework import generics
from rest_framework.mixins import RetrieveModelMixin
from diamm.serializers.website.tag import TagSerializer
from diamm.models.site.tag import Tag


class TagDetail(generics.RetrieveAPIView):
    template_name = "website/tag/tag_detail.jinja2"
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
