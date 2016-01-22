from django.db import models

class LegacyDiammUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=20, blank=True, null=True)
    displayname = models.CharField(db_column='displayName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    passwd = models.CharField(max_length=80, blank=True, null=True)
    email = models.CharField(max_length=80, blank=True, null=True)
    affiliation = models.CharField(max_length=200, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'DiammUser'
        app_label = "diamm_migrate"
