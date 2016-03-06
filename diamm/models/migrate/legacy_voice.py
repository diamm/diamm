from django.db import models


class LegacyVoice(models.Model):
    class Meta:
        managed = False
        db_table = 'alVoice'
        app_label = "diamm_migrate"


    alvoicekey = models.IntegerField(db_column='alVoiceKey', primary_key=True)  # Field name made lowercase.
    voice = models.TextField(blank=True, null=True)
