from django.db import models


class LegacySourceCopyist(models.Model):
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alcopyistkey = models.DecimalField(db_column='alcopyistKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alcopyisttypekey = models.DecimalField(db_column='alcopyistTypeKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    attribution_uncertain = models.TextField(blank=True, null=True)
    sourcecopyistkey = models.IntegerField(db_column='sourceCopyistKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Source_Copyist_IS'
        app_label = "diamm_migrate"
