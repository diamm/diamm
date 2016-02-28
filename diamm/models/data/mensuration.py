from django.db import models


class Mensuration(models.Model):
    class Meta:
        app_label = "diamm_data"

    sign = models.CharField(max_length=64, blank=True, null=True)
    text = models.CharField(max_length=256)

    def __str__(self):
        return self.text
