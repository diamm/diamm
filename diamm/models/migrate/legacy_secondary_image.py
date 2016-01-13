from django.db import models


class LegacySecondaryImage(models.Model):
    secondaryimagekey = models.IntegerField(db_column='secondaryImageKey', primary_key=True)  # Field name made lowercase.
    imagekey = models.DecimalField(db_column='ImageKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    filename = models.TextField(blank=True, null=True)
    imagetype = models.TextField(blank=True, null=True)
    archivefilename = models.TextField(blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    datemodified = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SecondaryImage'
        app_label = "diamm_migrate"
