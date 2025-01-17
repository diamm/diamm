from django.db import models


class Cycle(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("title",)

    title = models.CharField(max_length=256)
    composer = models.ForeignKey(
        "diamm_data.Person", blank=True, null=True, on_delete=models.CASCADE
    )
    type = models.ForeignKey("diamm_data.CycleType", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"

    @property
    def anonymous(self):
        return self.composer is None
