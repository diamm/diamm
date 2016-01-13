from django.db import models


class LegacyComposition(models.Model):
    compositionkey = models.IntegerField(db_column='compositionKey', primary_key=True)  # Field name made lowercase.
    genre = models.TextField(blank=True, null=True)
    max_number_of_voices = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    composition_name = models.TextField(blank=True, null=True)
    isorhythmic = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Composition'
        app_label = "diamm_migrate"
