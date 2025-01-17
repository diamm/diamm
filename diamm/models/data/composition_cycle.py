from django.db import models


class CompositionCycle(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("order",)

    composition = models.ForeignKey(
        "diamm_data.Composition", related_name="cycles", on_delete=models.CASCADE
    )
    cycle = models.ForeignKey(
        "diamm_data.Cycle", related_name="compositions", on_delete=models.CASCADE
    )
    order = models.IntegerField(blank=True, null=True)
