from django.db import models


class CycleType(models.Model):
    class Meta:
        app_label = "diamm_data"

    name = models.CharField(max_length=256)

    def __str__(self):
        return "{0}".format(self.name)
