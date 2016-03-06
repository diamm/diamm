from django.db import models


class LegacyMensuration(models.Model):
    class Meta:
        managed = False
        db_table = 'alMensuration'
        app_label = "diamm_migrate"

    almensurationkey = models.IntegerField(db_column='alMensurationKey', primary_key=True)  # Field name made lowercase.
    mensurationsign = models.TextField(db_column='mensurationSign', blank=True, null=True)  # Field name made lowercase.
    mensurationtext = models.TextField(db_column='mensurationText', blank=True, null=True)  # Field name made lowercase.

