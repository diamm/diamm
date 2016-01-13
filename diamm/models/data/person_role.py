from django.db import models


class PersonRole(models.Model):
    class Meta:
        app_label = "diamm_data"

    person = models.ForeignKey("diamm_data.Person")
    role = models.ForeignKey("diamm_data.Role")
    earliest_year = models.IntegerField(blank=True, null=True)
    latest_year = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
