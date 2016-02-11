from django.db import models


class PageCondition(models.Model):
    class Meta:
        app_label = "diamm_data"

    # Primary Keys. See fixtures/page_conditions.json for initial data
    REQUIRES_UV = 1
    REQUIRES_ENHANCEMENT = 2
    PALIMPSEST = 3
    OFFSET = 4
    BADLY_DAMAGED = 5
    CROPPED = 6
    WATER_STAINED = 7
    SHOW_THROUGH = 8
    BURN_THROUGH = 9
    GOOD = 10
    MILD_TWEAKING = 11
    MODERATE = 12
    POOR = 13
    VERY_POOR = 14
    ILLEGIBLE = 15

    condition = models.CharField(max_length=256)

    def __str__(self):
        return "{0}".format(self.condition)
