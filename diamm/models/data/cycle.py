from django.db import models


class Cycle(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("title",)

    title = models.CharField(max_length=256)
    # ORM convenience (doesn’t create a table because `through` is explicit)
    composers = models.ManyToManyField(
        "diamm_data.Person",
        through="diamm_data.CycleComposer",
        related_name="composed_cycles",
    )
    type = models.ForeignKey("diamm_data.CycleType", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"

    @property
    def anonymous(self):
        return self.composer is None
