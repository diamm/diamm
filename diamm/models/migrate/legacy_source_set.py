from django.db import models


class LegacySourceSet(models.Model):
    class Meta:
        app_label = "diamm_migrate"
        managed = False
        db_table = 'SourceSet_IS'

    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    setkey = models.DecimalField(db_column='setKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    sourcesetkey = models.IntegerField(db_column='sourceSetKey', primary_key=True)  # Field name made lowercase.
