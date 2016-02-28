from django.db import models


class Clef(models.Model):
    class Meta:
        app_label = "diamm_data"

    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name
