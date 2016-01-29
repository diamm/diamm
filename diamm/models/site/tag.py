from django.db import models


class Tag(models.Model):
    class Meta:
        app_label = "diamm_site"

    tag = models.CharField(max_length=64)

