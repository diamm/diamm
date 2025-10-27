from django.db import models
from django.utils.text import Truncator


class Text(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("incipit", "id")

    text = models.TextField()
    incipit = models.CharField(max_length=256, blank=True, null=True)
    legacy_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        if self.incipit:
            return self.incipit
        else:
            return Truncator(self.text).words(15, truncate=" ...")
