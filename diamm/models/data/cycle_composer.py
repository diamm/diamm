from django.db import models


class CycleComposer(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("cycle__title",)
        constraints = [
            models.UniqueConstraint(
                fields=("cycle", "composer"),
                name="uniq_cyclecomposer_cycle_composer",
            ),
        ]

    cycle = models.ForeignKey("diamm_data.Cycle", on_delete=models.CASCADE)

    composer = models.ForeignKey(
        "diamm_data.Person", related_name="cycles", on_delete=models.CASCADE
    )
    uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    @property
    def composer_name(self):
        return self.composer.full_name
