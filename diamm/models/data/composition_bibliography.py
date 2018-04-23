from django.db import models


class CompositionBibliography(models.Model):
    class Meta:
        app_label = "diamm_data"

    composition = models.ForeignKey("diamm_data.Composition",
                                    related_name="bibliography",
                                    on_delete=models.CASCADE)
    bibliography = models.ForeignKey("diamm_data.Bibliography",
                                     related_name="compositions",
                                     on_delete=models.CASCADE)
    pages = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

