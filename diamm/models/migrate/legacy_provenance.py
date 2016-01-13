from django.db import models


class LegacyProvenance(models.Model):
    alprovenancekey = models.IntegerField(db_column='alProvenanceKey', primary_key=True)  # Field name made lowercase.
    country = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alProvenance'
        app_label = "diamm_migrate"
