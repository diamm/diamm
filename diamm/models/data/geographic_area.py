from django.db import models
from simple_history.models import HistoricalRecords

# Define here so they can be used outside of the module
CITY = 1
COUNTRY = 2
STATE = 3
REGION = 4
FICTIONAL = 5


class GeographicArea(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ['name']

    REGION_TYPES = (
        (CITY, "City"),
        (COUNTRY, "Country"),
        (STATE, "County/Province/State/Canton"),
        (REGION, "Region/Cultural area"),
        (FICTIONAL, "Fictional/Imaginary")
    )

    name = models.CharField(max_length=255)
    type = models.IntegerField(choices=REGION_TYPES)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               help_text="""If the area is subordinate to another (e.g., city to country),
                               you can specify this here.""")

    # Legacy ID is composed of the legacy model and the PK, so 'legacy_city.4' or 'legacy_country.10'
    # This provides cross referencing between new and old objects.
    legacy_id = models.CharField(max_length=128, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.parent:
            return "{0} ({1})".format(self.name, self.parent.name)
        return "{0}".format(self.name)

    @property
    def area_type(self):
        if self.type == CITY:
            return "City"
        elif self.type == COUNTRY:
            return "Country"
        elif self.type == STATE:
            return "County/Province/State/Canton"
        elif self.type == REGION:
            return "Region/Cultural area"
        elif self.type == FICTIONAL:
            return "Fictional/Imaginary"
