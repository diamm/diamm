from django.db import models


class CompositionCycle(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('order',)

    composition = models.ForeignKey("diamm_data.Composition", related_name="cycles")
    cycle = models.ForeignKey("diamm_data.Cycle", related_name="compositions")
    order = models.IntegerField(blank=True, null=True)

