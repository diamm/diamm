from django.db import models


class PersonRole(models.Model):
    class Meta:
        app_label = "diamm_data"

    person = models.ForeignKey("diamm_data.Person",
                               related_name="roles")
    role = models.ForeignKey("diamm_data.Role",
                             related_name="people")
    earliest_year = models.IntegerField(blank=True, null=True)
    earliest_year_uncertain = models.BooleanField(default=False)
    latest_year = models.IntegerField(blank=True, null=True)
    latest_year_uncertain = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)

    def full_role(self):
        pass
