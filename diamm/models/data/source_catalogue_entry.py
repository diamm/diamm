from django.db import models


class SourceCatalogueEntry(models.Model):
    """
        Tracks the scanned catalogue entries from RISM
        for sources.
    """
    class Meta:
        app_label = "diamm_data"
        verbose_name_plural = "Source Catalogue Entries"
        ordering = ('entry',)

    order = models.IntegerField(default=1)
    entry = models.CharField(max_length=16)
    source = models.ForeignKey("diamm_data.Source",
                               related_name="catalogue_entries")

    def __str__(self):
        return "{0}".format(self.entry)
