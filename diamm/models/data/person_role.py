from django.db import models


class PersonRole(models.Model):
    class Meta:
        app_label = "diamm_data"

    person = models.ForeignKey("diamm_data.Person",
                               related_name="roles",
                               on_delete=models.CASCADE)
    role = models.ForeignKey("diamm_data.Role",
                             related_name="people",
                             on_delete=models.CASCADE)
    earliest_year = models.IntegerField(blank=True, null=True)
    earliest_year_approximate = models.BooleanField(default=False)
    latest_year = models.IntegerField(blank=True, null=True)
    latest_year_approximate = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        early_pfx = ""
        late_pfx = ""
        if self.earliest_year_approximate:
            early_pfx = "ca. "
        if self.latest_year_approximate:
            late_pfx = "ca. "
        early_year = "{0}".format(self.earliest_year) if self.earliest_year else ""
        late_year = "{0}".format(self.latest_year) if self.latest_year else ""

        date_str = ""
        if early_year or late_year:
            date_str = "{epfx}{early}–{lpfx}{late}".format(epfx=early_pfx,
                                                           early=early_year,
                                                           lpfx=late_pfx,
                                                           late=late_year)

        if date_str:
            return "{0} ({1})".format(self.role, date_str)
        else:
            return "{0}".format(self.role)

    @property
    def role_description(self):
        return self.__str__()
