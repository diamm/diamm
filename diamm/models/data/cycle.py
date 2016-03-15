from django.db import models


class Cycle(models.Model):
    class Meta:
        app_label = "diamm_data"

    title = models.CharField(max_length=256)
    composer = models.ForeignKey("diamm_data.Person", blank=True, null=True)
    type = models.ForeignKey("diamm_data.CycleType")

    def __str__(self):
        return "{0}".format(self.title)
