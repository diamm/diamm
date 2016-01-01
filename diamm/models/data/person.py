from django.db import models
from simple_history.models import HistoricalRecords


class Person(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name_plural = "People"
        ordering = ["last_name", "first_name"]

    last_name = models.CharField(max_length=512,
                                 help_text="Last name, or full name if it does not follow modern conventions, e.g., 'Louis of Bavaria'")
    first_name = models.CharField(max_length=512, blank=True, null=True)
    title = models.CharField(max_length=512, blank=True, null=True,
                             help_text="Personal title, e.g., Duke, Count, Pope.")
    earliest_year = models.IntegerField(blank=True, null=True)
    latest_year = models.IntegerField(blank=True, null=True)
    legacy_id = models.CharField(max_length=64)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.first_name:
            return "{0}, {1}".format(self.last_name, self.first_name)
        else:
            return "{0}".format(self.last_name)
