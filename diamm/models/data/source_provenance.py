from django.db import models


class SourceProvenance(models.Model):
    class Meta:
        app_label = "diamm_data"

    source = models.ForeignKey("diamm_data.Source",
                               related_name="provenance")

    city = models.ForeignKey("diamm_data.GeographicArea",
                             related_name="city_sources", blank=True, null=True)
    country = models.ForeignKey("diamm_data.GeographicArea",
                                related_name="country_sources", blank=True, null=True)
    region = models.ForeignKey("diamm_data.GeographicArea",
                               related_name="region_sources", blank=True, null=True)
    protectorate = models.ForeignKey("diamm_data.GeographicArea",
                                     related_name="protectorate_sources",
                                     blank=True, null=True)

    organization = models.ForeignKey("diamm_data.Organization", blank=True, null=True)
    uncertain = models.BooleanField(default=False)
    earliest_year = models.IntegerField(blank=True, null=True)
    latest_year = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
