from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SourceProvenance(models.Model):
    class Meta:
        app_label = "diamm_data"

    source = models.ForeignKey("diamm_data.Source",
                               related_name="provenance")

    city = models.ForeignKey("diamm_data.GeographicArea",
                             related_name="city_sources", blank=True, null=True)
    city_uncertain = models.BooleanField(default=False)

    country = models.ForeignKey("diamm_data.GeographicArea",
                                related_name="country_sources", blank=True, null=True)
    country_uncertain = models.BooleanField(default=False)

    region = models.ForeignKey("diamm_data.GeographicArea",
                               related_name="region_sources", blank=True, null=True)
    region_uncertain = models.BooleanField(default=False)
    protectorate = models.ForeignKey("diamm_data.GeographicArea",
                                     related_name="protectorate_sources",
                                     blank=True, null=True)

    earliest_year = models.IntegerField(blank=True, null=True)
    latest_year = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    # Generic foreign keys to relate to people and organizations. This is optional.
    limit = models.Q(app_label='diamm_data', model="person") | models.Q(app_label='diamm_data', model='organization')
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to=limit,
                                     blank=True,
                                     null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    entity = GenericForeignKey()
    entity_uncertain = models.BooleanField(default=False)
