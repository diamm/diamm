from django.db import models


class Text(models.Model):
    class Meta:
        app_label = "diamm_data"

    text = models.TextField()
    title = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.title
