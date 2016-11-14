from django.db import models


class ItemBibliography(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name_plural = "Item Bibliographies"
        ordering = ("bibliography__year asc",)

    item = models.ForeignKey("diamm_data.Item")
    bibliography = models.ForeignKey("diamm_data.Bibliography")
    pages = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
