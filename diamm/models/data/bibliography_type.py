from django.db import models


class BibliographyType(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('name',)

    name = models.CharField(max_length=512)

    def __str__(self):
        return "{0}".format(self.name)
