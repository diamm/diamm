from django.db import models


class LegacySet(models.Model):
    class Meta:
        app_label = "diamm_migrate"
        managed = False
        db_table = 'Set'

    setkey = models.IntegerField(db_column='setKey', primary_key=True)  # Field name made lowercase.
    clustershelfmark = models.TextField(db_column='clusterShelfMark', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)
    bibliography = models.TextField(blank=True, null=True)
    settypekey = models.DecimalField(db_column='setTypeKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    g_key = models.DecimalField(db_column='g_Key', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
