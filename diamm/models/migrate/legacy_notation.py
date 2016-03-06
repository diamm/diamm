from django.db import models


class LegacyNotation(models.Model):
    alnotationtypekey = models.IntegerField(primary_key=True)
    notation_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alNotationType'
        app_label = "diamm_migrate"

