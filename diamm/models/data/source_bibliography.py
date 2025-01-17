from django.db import models


class SourceBibliography(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name_plural = "Source bibliographies"
        # ordering = ('bibliography__authors__bibliography_author__last_name',)

    source = models.ForeignKey(
        "diamm_data.Source", related_name="bibliographies", on_delete=models.CASCADE
    )
    bibliography = models.ForeignKey(
        "diamm_data.Bibliography", related_name="sources", on_delete=models.CASCADE
    )
    primary_study = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    pages = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.bibliography.title}"
