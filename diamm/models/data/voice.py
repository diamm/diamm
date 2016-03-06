from django.db import models


class Voice(models.Model):
    class Meta:
        app_label = "diamm_data"

    label = models.CharField(max_length=256, blank=True, null=True)
    position = models.CharField(max_length=256, blank=True, null=True)
    type = models.ForeignKey("diamm_data.VoiceType")
    item = models.ForeignKey("diamm_data.Item")
    languages = models.ManyToManyField("diamm_data.Language")
    mensuration = models.ForeignKey("diamm_data.Mensuration", blank=True, null=True)
    clef = models.ForeignKey("diamm_data.Clef", blank=True, null=True)

    voice_text = models.TextField(blank=True, null=True)
    standard_text = models.ForeignKey("diamm_data.Text", blank=True, null=True)
    legacy_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return "{0} [{1}]".format(
            str(self.item),
            self.type.name
        )
