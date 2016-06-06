from rest_framework import views
from rest_framework.response import Response
from diamm.models.site.story import Story
from diamm.models.data.source import Source
from diamm.models.data.archive import Archive
from diamm.serializers.website.story import StorySerializer


class HomeView(views.APIView):
    template_name = "index.jinja2"

    def _counts(self):
        num_sources = Source.objects.count()
        num_archives = Archive.objects.count()

        return {
            'num_sources': num_sources,
            'num_archives': num_archives
        }


    def get(self, request, *args, **kwargs):
        news_stories = Story.objects.order_by('created')[:3]
        news_stories_data = StorySerializer(news_stories,
                                            context={'request': request},
                                            many=True).data

        return Response({
            'stories': news_stories_data,
            'counts': self._counts()
        })
