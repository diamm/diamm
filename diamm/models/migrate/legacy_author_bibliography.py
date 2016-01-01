from django.db import models


class LegacyAuthorBibliography(models.Model):
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alauthorkey = models.DecimalField(db_column='alAuthorKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    author_editor = models.TextField(blank=True, null=True)
    authorbibliography = models.IntegerField(db_column='authorBibliography', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AuthorBibliography_IS'
        app_label = "diamm_migrate"
