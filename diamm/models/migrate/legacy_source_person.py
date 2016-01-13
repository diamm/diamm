from django.db import models


class LegacySourcePerson(models.Model):
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alpersonkey = models.DecimalField(db_column='alPersonKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alpersonrelationshipkey = models.DecimalField(db_column='alPersonRelationshipKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    attribution_uncertain = models.TextField(blank=True, null=True)
    sourcealpersonkey = models.IntegerField(db_column='sourceAlPersonKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Source_Person_IS'
        app_label = "diamm_migrate"
