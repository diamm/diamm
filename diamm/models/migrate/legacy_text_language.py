from django.db import models


class LegacyTextLanguage(models.Model):
    class Meta:
        managed = False
        db_table = 'TextLanguage_IS'
        app_label = "diamm_migrate"

    allanguagekey = models.DecimalField(db_column='alLanguageKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    textkey = models.DecimalField(db_column='textKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    textlanguagekey = models.IntegerField(db_column='textLanguageKey', primary_key=True)  # Field name made lowercase.
