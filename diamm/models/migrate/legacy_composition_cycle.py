from django.db import models


class LegacyCompositionCycle(models.Model):
    class Meta:
        managed = False
        db_table = 'CompositionCycle'
        app_label = "diamm_migrate"

    compositioncyclekey = models.IntegerField(db_column='compositionCycleKey', primary_key=True)  # Field name made lowercase.
    title = models.TextField(blank=True, null=True)
    title_model_compositionkey = models.DecimalField(db_column='title_model_compositionKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    composerkey = models.DecimalField(db_column='composerKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    composer = models.TextField(blank=True, null=True)
    alcycletypekey = models.DecimalField(db_column='alCycleTypeKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
