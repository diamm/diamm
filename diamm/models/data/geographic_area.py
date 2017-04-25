from django.db import models


class GeographicArea(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ['name']

    CITY = 1
    COUNTRY = 2
    STATE = 3
    REGION = 4
    FICTIONAL = 5

    REGION_TYPES = (
        (CITY, "City"),
        (COUNTRY, "Country"),
        (STATE, "County/Province/State/Canton"),
        (REGION, "Region/Cultural area/Protectorate"),
        (FICTIONAL, "Fictional/Imaginary")
    )

    name = models.CharField(max_length=255)
    type = models.IntegerField(choices=REGION_TYPES, help_text="""The region type.""")
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               help_text="""If the area is subordinate to another (e.g., city to country),
                               you can specify this here. For regions where their historical provenance has changed 
                               (e.g., Alsace and France or Germany; Vienna and Austria or Prussia), you should choose the
                               current affiliation.""")
    variant_names = models.CharField(max_length=255, blank=True, null=True, help_text="Separate names with a comma.")

    # Legacy ID is composed of the legacy model and the PK, so 'legacy_city.4' or 'legacy_country.10'
    # This provides cross referencing between new and old objects.
    legacy_id = models.ManyToManyField("diamm_data.LegacyId")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}".format(self.name)

    @property
    def cities(self):
        """
        NB: For non-country objects, this method will return an empty set.
        :return: A queryset containing the cities that are related to a parent country
        """
        return self.geographicarea_set.filter(type=self.CITY)

    @property
    def regions(self):
        """
        NB: For non-country objects, this method will return an empty set.
        :return: A queryset containing the regions that are related to a parent country
        """
        return self.geographicarea_set.filter(type=self.REGION)

    @property
    def states(self):
        """
        NB: For non-country objects, this method will return an empty set.
        :return: A queryset containing the regions that are related to a parent country.
        """
        return self.geographicarea_set.filter(type=self.STATE)

    @property
    def area_type(self):
        if self.type == self.CITY:
            return "City"
        elif self.type == self.COUNTRY:
            return "Country"
        elif self.type == self.STATE:
            return "County/Province/State/Canton"
        elif self.type == self.REGION:
            return "Region/Cultural area"
        elif self.type == self.FICTIONAL:
            return "Fictional/Imaginary"
