from rest_framework import generics
from diamm.models.site.story import Story
from diamm.serializers.website.story import StorySerializer


class StoryDetail(generics.RetrieveAPIView):
    template_name = "website/story/story_detail.jinja2"
    queryset = Story.objects.all()
    serializer_class = StorySerializer
