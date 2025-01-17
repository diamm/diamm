from django.db import models


class SourceCatalogueEntry(models.Model):
    """
    Tracks the scanned catalogue entries from RISM
    for sources.
    """

    class Meta:
        app_label = "diamm_data"
        verbose_name_plural = "Source catalogue entries"
        ordering = ("entry",)

    order = models.IntegerField(default=1)
    entry = models.CharField(max_length=16)
    source = models.ForeignKey(
        "diamm_data.Source", related_name="catalogue_entries", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.entry}"
