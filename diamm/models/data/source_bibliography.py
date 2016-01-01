from django.db import models


class SourceBibliography(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('bibliography__authors__last_name',)

    source = models.ForeignKey("diamm_data.Source")
    bibliography = models.ForeignKey("diamm_data.Bibliography")
    notes = models.TextField(blank=True, null=True)
    pages = models.TextField(blank=True, null=True)
