from django.db import models


class Voice(models.Model):
    class Meta:
        app_label = "diamm_data"

    type = models.ForeignKey("diamm_data.VoiceType")
    mensuration = models.ForeignKey("diamm_data.Mensuration", blank=True, null=True)
    clef = models.ForeignKey("diamm_data.Clef", blank=True, null=True)

    untexted = models.BooleanField(default=False)
    voice_text = models.TextField(blank=True, null=True)
    standard_text = models.ForeignKey("diamm_data.Text", blank=True, null=True)
