from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SourceRelationship(models.Model):
    """
        Tracks a relationship with either a person or an organization.

        This is implemented using GenericForeignKeys to a Person or Organization object.
    """
    class Meta:
        app_label = "diamm_data"

    limit = models.Q(app_label='diamm_data', model="person") | models.Q(app_label='diamm_data', model='organization')

    source = models.ForeignKey("diamm_data.Source",
                               related_name="relationships")

    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to=limit)

    object_id = models.PositiveIntegerField()
    related_entity = GenericForeignKey()

    relationship_type = models.ForeignKey("diamm_data.SourceRelationshipType")
    uncertain = models.BooleanField(default=False)
