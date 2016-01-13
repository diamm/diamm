from django.db import models


class Bibliography(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name = "Bibliography Entry"
        verbose_name_plural = "Bibliography Entries"
        ordering = ('authors__last_name',)

    title = models.CharField(max_length=1024)
    authors = models.ManyToManyField("diamm_data.BibliographyAuthor",
                                     through="diamm_data.BibliographyAuthorRole")
    year = models.CharField(max_length=256, blank=True, null=True)
    type = models.ForeignKey("diamm_data.BibliographyType")
    abbreviation = models.CharField(max_length=128, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{0}".format(self.abbreviation)
