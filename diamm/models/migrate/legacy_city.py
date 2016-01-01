from django.db import models


class LegacyCity(models.Model):
    country = models.ForeignKey("diamm_migrate.LegacyCountry",
                                db_column='alCountryKey',
                                blank=True, null=True)  # Field name made lowercase.

    city = models.TextField(blank=True, null=True)
    id = models.IntegerField(db_column='alCityKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alCity'
        app_label = "diamm_migrate"
