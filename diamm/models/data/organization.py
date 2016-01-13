from django.db import models


class Organization(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('name',)

    name = models.CharField(max_length=1024, default="s.n.")
    type = models.ForeignKey("diamm_data.OrganizationType", default=1)
    legacy_id = models.CharField(max_length=64, blank=True, null=True)
    location = models.ForeignKey("diamm_data.GeographicArea", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}".format(self.name)
