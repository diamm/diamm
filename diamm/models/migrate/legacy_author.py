from django.db import models


class LegacyAuthor(models.Model):
    alauthorkey = models.IntegerField(db_column='alAuthorKey', primary_key=True)  # Field name made lowercase.
    lastname = models.TextField(db_column='lastName', blank=True, null=True)  # Field name made lowercase.
    firstname = models.TextField(db_column='firstName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alAuthor'
        app_label = "diamm_migrate"
