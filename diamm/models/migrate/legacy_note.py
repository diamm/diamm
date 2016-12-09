from django.db import models


class LegacyNote(models.Model):
    class Meta:
        managed = False
        db_table = 'Note'
        app_label = "diamm_migrate"

    legacy_id = models.IntegerField(blank=True, null=True)
    notetype = models.IntegerField(db_column='noteType', blank=True, null=True)  # Field name made lowercase.
    notetext = models.TextField(db_column='noteText', blank=True, null=True)  # Field name made lowercase.
    user = models.IntegerField(blank=True, null=True)
    visibility = models.IntegerField(blank=True, null=True)
    datemodified = models.DateTimeField(db_column='dateModified', blank=True, null=True)  # Field name made lowercase.
    sourcekey = models.IntegerField(db_column='sourceKey', blank=True, null=True)  # Field name made lowercase.
    imagekey = models.IntegerField(db_column='imageKey', blank=True, null=True)  # Field name made lowercase.
