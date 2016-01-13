from django.db import models


class LegacyLanguage(models.Model):
    allangaugekey = models.IntegerField(db_column='alLangaugeKey', primary_key=True)  # Field name made lowercase.
    language = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alLanguage'
        app_label = "diamm_migrate"
