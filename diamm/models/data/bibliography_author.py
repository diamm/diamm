from django.db import models


class BibliographyAuthor(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('last_name', 'first_name')

    last_name = models.CharField(max_length=512)
    first_name = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        if self.first_name:
            return "{0}, {1}".format(self.last_name, self.first_name)
        return "{0}".format(self.last_name)

    @property
    def full_name(self):
        return str(self)
