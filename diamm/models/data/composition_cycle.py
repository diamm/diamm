from django.db import models


class CompositionCycle(models.Model):
    class Meta:
        app_label = "diamm_data"

    composition = models.ForeignKey("diamm_data.Composition")
    cycle = models.ForeignKey("diamm_data.Cycle")
    order = models.IntegerField(blank=True, null=True)

