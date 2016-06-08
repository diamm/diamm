from rest_framework import serializers
from diamm.models.site.contribution import Contribution


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = ('summary', 'record', 'object_id', 'content_type', 'summary', 'updated', 'contributor')
