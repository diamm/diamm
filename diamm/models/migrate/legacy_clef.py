from django.db import models


class LegacyClef(models.Model):
    class Meta:
        managed = False
        db_table = 'alClef'
        app_label = "diamm_migrate"

    alclefkey = models.IntegerField(db_column='alClefKey', primary_key=True)  # Field name made lowercase.
    clef = models.TextField(blank=True, null=True)
