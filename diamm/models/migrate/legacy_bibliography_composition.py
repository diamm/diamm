from django.db import models


class LegacyBibliographyComposition(models.Model):
    compositionkey = models.DecimalField(db_column='compositionKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    biblabbrev = models.TextField(db_column='biblAbbrev', blank=True, null=True)  # Field name made lowercase.
    bibliographycompositionkey = models.IntegerField(db_column='bibliographyCompositionKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BiblComposition_IS'
        app_label = "diamm_migrate"
