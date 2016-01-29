from django.db import models


class Story(models.Model):
    class Meta:
        app_label = "diamm_site"

    title = models.CharField(max_length=256)
    body = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
