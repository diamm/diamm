from django.db import models


class Notation(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('name',)

    name = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
