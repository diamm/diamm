from django.db import models


class LegacyBibliographySource(models.Model):
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    page = models.TextField(blank=True, null=True)
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    biblabbrev = models.TextField(db_column='BiblAbbrev', blank=True, null=True)  # Field name made lowercase.
    bibliographysourcekey = models.IntegerField(db_column='bibliographySourceKey', primary_key=True)  # Field name made lowercase.
    composerkey = models.DecimalField(db_column='composerKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    primarystudy = models.TextField(db_column='primaryStudy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BibliographySource_IS'
        app_label = "diamm_migrate"
