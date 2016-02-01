from rest_framework import serializers
from diamm.models.site.story import Story


class StorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Story
