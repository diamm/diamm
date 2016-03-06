from django.db import models

class LegacySourceNotation(models.Model):
    class Meta:
        managed = False
        db_table = 'NotationSource_IS'
        app_label = "diamm_migrate"

    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alnotationtypekey = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    notationsourcekey = models.IntegerField(db_column='notationsourceKey', primary_key=True)  # Field name made lowercase.
