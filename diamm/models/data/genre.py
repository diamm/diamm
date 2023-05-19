from django.db import models


class Genre(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('name',)

    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name}"
