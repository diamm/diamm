from django.db import models
from django.db.models.functions.text import Lower


class Genre(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = (Lower("name"),)

    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name}"
