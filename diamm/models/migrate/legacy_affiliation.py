from django.db import models


class LegacyAffiliation(models.Model):
    alaffiliationkey = models.IntegerField(db_column='alaffiliationKey', primary_key=True)  # Field name made lowercase.
    affiliation = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alAffiliation'
        app_label = "diamm_migrate"
