from django.db import models


class LegacyCompositionCycleComposition(models.Model):
    class Meta:
        managed = False
        db_table = 'CompositionCycleComposition'
        app_label = "diamm_migrate"

    compositioncyclekey = models.DecimalField(db_column='compositionCycleKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    compositionkey = models.DecimalField(db_column='compositionKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    positiontitle = models.TextField(db_column='positionTitle', blank=True, null=True)  # Field name made lowercase.
    compositioncyclecompositionkey = models.IntegerField(db_column='compositionCycleCompositionKey', primary_key=True)  # Field name made lowercase.
    orderno = models.DecimalField(db_column='orderNo', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
