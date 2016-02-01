from rest_framework import views
from rest_framework.response import Response
from diamm.models.site.story import Story
from diamm.serializers.website.story import StorySerializer


class HomeView(views.APIView):
    template_name = "index.jinja2"

    def get(self, request, *args, **kwargs):
        news_stories = Story.objects.order_by('created')[:3]
        news_stories_data = StorySerializer(news_stories,
                                            context={'request': request},
                                            many=True)

        return Response({
            'stories': news_stories_data.data
        })
