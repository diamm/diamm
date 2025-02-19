from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class SourceProvenance(models.Model):
    class Meta:
        app_label = "diamm_data"

    source = models.ForeignKey(
        "diamm_data.Source", related_name="provenance", on_delete=models.CASCADE
    )

    city = models.ForeignKey(
        "diamm_data.GeographicArea",
        related_name="city_sources",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    city_uncertain = models.BooleanField(default=False)

    country = models.ForeignKey(
        "diamm_data.GeographicArea",
        related_name="country_sources",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    country_uncertain = models.BooleanField(default=False)

    region = models.ForeignKey(
        "diamm_data.GeographicArea",
        related_name="region_sources",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    region_uncertain = models.BooleanField(default=False)
    protectorate = models.ForeignKey(
        "diamm_data.GeographicArea",
        related_name="protectorate_sources",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    earliest_year = models.IntegerField(blank=True, null=True)
    latest_year = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    # Generic foreign keys to relate to people and organizations. This is optional.
    limit = models.Q(app_label="diamm_data", model="person") | models.Q(
        app_label="diamm_data", model="organization"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit,
        blank=True,
        null=True,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    entity = GenericForeignKey()
    entity_uncertain = models.BooleanField(default=False)

    def __str__(self):
        source_name = self.source.display_name
        places = filter(None, [self.city, self.country, self.protectorate, self.region])
        places = [str(x) for x in places]
        return f"{source_name} ({', '.join(places)})"
