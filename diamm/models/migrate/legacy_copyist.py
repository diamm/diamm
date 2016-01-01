from django.db import models


class LegacyCopyist(models.Model):
    alcopyistkey = models.IntegerField(db_column='alcopyistKey', primary_key=True)  # Field name made lowercase.
    copyistname = models.TextField(db_column='copyistName', blank=True, null=True)  # Field name made lowercase.
    alaffiliationkey = models.DecimalField(db_column='alaffiliationKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alCopyist'
        app_label = "diamm_migrate"

