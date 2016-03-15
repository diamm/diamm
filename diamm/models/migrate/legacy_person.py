from django.db import models


class LegacyPerson(models.Model):
    alpersonkey = models.IntegerField(db_column='alPersonKey', primary_key=True)  # Field name made lowercase.
    alaffiliationkey = models.TextField(db_column='alaffiliationKey', blank=True, null=True)  # Field name made lowercase.
    fullnameoriginal = models.TextField(db_column='fullNameOriginal', blank=True, null=True)  # Field name made lowercase.
    firstname = models.TextField(blank=True, null=True)
    surname = models.TextField(db_column='Surname', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    startdate_approx = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    enddate_approx = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    enddate = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    aliases = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alPerson'
        app_label = "diamm_migrate"
