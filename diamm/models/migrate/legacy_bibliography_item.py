from django.db import models

class LegacyBibliographyItem(models.Model):
    class Meta:
        managed = False
        db_table = 'BiblItem_IS'
        app_label = "diamm_migrate"

    itemkey = models.DecimalField(db_column='itemKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    biblabbrev = models.TextField(db_column='biblAbbrev', blank=True, null=True)  # Field name made lowercase.
    bibliographyitemkey = models.IntegerField(db_column='bibliographyItemKey', primary_key=True)  # Field name made lowercase.
