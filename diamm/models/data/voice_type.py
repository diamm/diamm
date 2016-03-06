from django.db import models


class VoiceType(models.Model):
    class Meta:
        app_label = "diamm_data"

    name = models.CharField(max_length=256)
    legacy_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name
