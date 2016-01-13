from django.db import models


class LegacyRelationshipType(models.Model):
    alpersonrelationshipkey = models.IntegerField(db_column='alPersonRelationshipKey', primary_key=True)  # Field name made lowercase.
    relationshiptype = models.TextField(db_column='relationshipType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alPersonRelationship'
        app_label = "diamm_migrate"
