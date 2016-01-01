from django.db import models


class LegacyCountry(models.Model):
    country = models.TextField(blank=True, null=True)
    id = models.IntegerField(db_column='alcountryKey', primary_key=True)  # Field name made lowercase.
    abbreviation = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alCountry'
        app_label = "diamm_migrate"
