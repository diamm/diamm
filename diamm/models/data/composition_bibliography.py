from django.db import models


class CompositionBibliography(models.Model):
    class Meta:
        app_label = "diamm_data"

    composition = models.ForeignKey("diamm_data.Composition", related_name="bibliography")
    bibliography = models.ForeignKey("diamm_data.Bibliography", related_name="compositions")
    pages = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

