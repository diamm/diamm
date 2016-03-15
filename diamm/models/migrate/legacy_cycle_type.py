from django.db import models


class LegacyCycleType(models.Model):
    class Meta:
        managed = False
        db_table = 'alCycleType'
        app_label = "diamm_migrate"

    alcycletypekey = models.IntegerField(db_column='alCycleTypeKey', primary_key=True)  # Field name made lowercase.
    cycletype = models.TextField(db_column='cycleType', blank=True, null=True)  # Field name made lowercase.
