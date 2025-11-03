from django.db import models


class AreaTypeChoices(models.IntegerChoices):
    CITY = 1, "City"
    COUNTRY = 2, "Country"
    STATE = 3, "County/Province/State/Canton"
    REGION = 4, "Region/Cultural area/Protectorate"
    FICTIONAL = 5, "Fictional/Imaginary"


class GeographicArea(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ["name"]

    name = models.CharField(max_length=255)
    type = models.IntegerField(
        choices=AreaTypeChoices.choices, help_text="""The region type."""
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="""If the area is subordinate to another (e.g., city to country),
                               you can specify this here. For regions where their historical provenance has changed
                               (e.g., Alsace and France or Germany; Vienna and Austria or Prussia), you should choose the
                               present affiliation.""",
    )
    variant_names = models.CharField(
        max_length=255, blank=True, null=True, help_text="Separate names with a comma."
    )

    # Legacy ID is composed of the legacy model and the PK, so 'legacy_city.4' or 'legacy_country.10'
    # This provides cross referencing between new and old objects.
    legacy_id = models.ManyToManyField("diamm_data.LegacyId", blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    @property
    def cities(self):
        """
        NB: For non-country objects, this method will return an empty set.
        :return: A queryset containing the cities that are related to a parent country
        """
        return self.geographicarea_set.filter(type=AreaTypeChoices.CITY)

    @property
    def regions(self):
        """
        NB: For non-country objects, this method will return an empty set.
        :return: A queryset containing the regions that are related to a parent country
        """
        return self.geographicarea_set.filter(type=AreaTypeChoices.REGION)

    @property
    def states(self):
        """
        NB: For non-country objects, this method will return an empty set.
        :return: A queryset containing the regions that are related to a parent country.
        """
        return self.geographicarea_set.filter(type=AreaTypeChoices.STATE)

    @property
    def area_type(self) -> str | None:
        if not self.type:
            return None
        d = dict(AreaTypeChoices.choices)
        return d[self.type]
