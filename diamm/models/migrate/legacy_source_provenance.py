from django.db import models


class LegacySourceProvenance(models.Model):
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alprovenancekey = models.DecimalField(db_column='alProvenanceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    uncertain = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    institution = models.TextField(blank=True, null=True)
    protectorate = models.TextField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    sourceprovenancekey = models.IntegerField(db_column='sourceProvenanceKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SourceProvenance_IS'
        app_label = "diamm_migrate"
