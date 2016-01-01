from django.db import models

class LegacyComposer(models.Model):
    lastname = models.TextField(db_column='lastNameOriginal', blank=True, null=True)  # Field name made lowercase.
    composerkey = models.IntegerField(db_column='composerKey', primary_key=True)  # Field name made lowercase.
    firstname = models.TextField(db_column='firstName', blank=True, null=True)  # Field name made lowercase.
    dates_public = models.TextField(blank=True, null=True)
    variantspellings = models.TextField(blank=True, null=True)
    tngentry = models.TextField(db_column='TNGentry', blank=True, null=True)  # Field name made lowercase.
    date_earliest = models.TextField(blank=True, null=True)
    date_latest = models.TextField(blank=True, null=True)
    date_floruit_earliest = models.TextField(blank=True, null=True)
    date_floruit_latest = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Composer'
        app_label = "diamm_migrate"
