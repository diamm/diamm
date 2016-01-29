import os
from django.db import models
from django.conf import settings


class CoverImages(models.Model):
    class Meta:
        app_label = "diamm_site"

    caption = models.CharField(max_length=256)
    description = models.TextField()
    image = models.ImageField(os.path.join(settings.UPLOAD_DIR, 'covers'),
                              help_text="Images must be 2000x400 pixels.")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
