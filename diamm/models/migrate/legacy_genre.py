from django.db import models


class LegacyGenre(models.Model):
    algenrekey = models.IntegerField(db_column='alGenreKey', primary_key=True)  # Field name made lowercase.
    genre = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alGenre'
        app_label = "diamm_migrate"
