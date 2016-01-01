from django.db import models


class LegacyPerson(models.Model):
    alpersonkey = models.IntegerField(db_column='alPersonKey', primary_key=True)  # Field name made lowercase.
    alaffiliationkey = models.TextField(db_column='alaffiliationKey', blank=True, null=True)  # Field name made lowercase.
    fullnameoriginal = models.TextField(db_column='fullNameOriginal', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alPerson'
        app_label = "diamm_migrate"
