from django.db import models


class SourceToSourceRelationshipType(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("forward_label",)

    forward_label = models.CharField(max_length=512)
    inverse_label = models.CharField(max_length=512)

    def __str__(self):
        return self.forward_label
