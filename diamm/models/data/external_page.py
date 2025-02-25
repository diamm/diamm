from django.db import models


class ExternalPage(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ["source__shelfmark", "sort_order"]

    source = models.ForeignKey(
        "diamm_data.Source", related_name="external_pages", on_delete=models.CASCADE
    )
    label = models.CharField(
        max_length=64,
        help_text="""The label from the IIIF Canvas""",
    )
    # This may be refactored to allow for multiple page sort orders, but for now we'll stick with one
    sort_order = models.DecimalField(
        default=0, blank=True, null=True, decimal_places=3, max_digits=100
    )
