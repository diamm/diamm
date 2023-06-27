from django.db import models


class OrganizationType(models.Model):
    class Meta:
        app_label = "diamm_data"

    name = models.CharField(max_length=512, default="None")

    def __str__(self):
        return f"{self.name}"
