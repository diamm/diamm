from django.db import models


class Voice(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("item__composition__title",)

    label = models.CharField(
        max_length=256, blank=True, null=True, help_text="Former Text voicepart field"
    )
    position = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="Former Text positiononpage field",
    )
    type = models.ForeignKey("diamm_data.VoiceType", on_delete=models.CASCADE)
    item = models.ForeignKey(
        "diamm_data.Item", related_name="voices", on_delete=models.CASCADE
    )
    languages = models.ManyToManyField("diamm_data.Language")
    mensuration = models.ForeignKey(
        "diamm_data.Mensuration", blank=True, null=True, on_delete=models.CASCADE
    )
    clef = models.ForeignKey(
        "diamm_data.Clef", blank=True, null=True, on_delete=models.CASCADE
    )

    sort_order = models.IntegerField(
        blank=True,
        null=True,
        help_text="Used to sort voices e.g., Soprano, Alto, Tenor, Bass",
    )
    voice_text = models.TextField(blank=True, null=True)
    standard_text = models.ForeignKey(
        "diamm_data.Text", blank=True, null=True, on_delete=models.CASCADE
    )
    legacy_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.item} [{self.type.name}]"
