from django.db import models


class Notation(models.Model):
    class Meta:
        app_label = "diamm_data"

    name = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return "{0}".format(self.name)
