from django.db import models


class SourcePerson(models.Model):
    class Meta:
        app_label = "diamm_data"

    source = models.ForeignKey("diamm_data.Source",
                               related_name="person_relationships")
    person = models.ForeignKey("diamm_data.Person",
                               related_name="source_relationships")
    relationship_type = models.ForeignKey("diamm_data.SourceRelationshipType")
    uncertain = models.BooleanField(default=False)
