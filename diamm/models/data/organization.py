from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from diamm.helpers.solr_helpers import SolrManager


class Organization(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("name",)

    ARCHIVE_HELP_TEXT = """
        If an organization has an equivalent entry in the Organizations table,
        enter it here and the two will be linked.
    """

    name = models.CharField(max_length=1024, default="s.n.")
    variant_names = models.CharField(max_length=1024, blank=True, null=True)
    type = models.ForeignKey(
        "diamm_data.OrganizationType", default=1, on_delete=models.CASCADE
    )
    legacy_id = models.CharField(max_length=64, blank=True, null=True)
    location = models.ForeignKey(
        "diamm_data.GeographicArea",
        blank=True,
        null=True,
        related_name="organizations",
        on_delete=models.CASCADE,
    )
    note = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    archive = models.ForeignKey(
        "diamm_data.Archive",
        blank=True,
        null=True,
        help_text=ARCHIVE_HELP_TEXT,
        on_delete=models.CASCADE,
    )

    sources_copied = GenericRelation("diamm_data.SourceCopyist")
    sources_related = GenericRelation("diamm_data.SourceRelationship")
    sources_provenance = GenericRelation("diamm_data.SourceProvenance")

    def __str__(self):
        return f"{self.name}"

    @property
    def solr_copyist(self):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = [
            "type:sourcecopyist",
            "copyist_type_s:organization",
            f"copyist_pk_i:{self.pk}",
        ]
        sort = "source_ans asc"
        connection.search("*:*", fq=fq, sort=sort, rows=100)

        return list(connection.results)

    @property
    def solr_relationships(self):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = [
            "type:sourcerelationship",
            "related_entity_type_s:organization",
            f"related_entity_pk_i:{self.pk}",
        ]
        sort = "source_ans asc"
        connection.search("*:*", fq=fq, sort=sort, rows=100)

        return list(connection.results)

    @property
    def solr_provenance(self):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = [
            "type:sourceprovenance",
            "entity_type_s:organization",
            f"entity_pk_i:{self.pk}",
        ]
        sort = "source_ans asc"
        connection.search("*:*", fq=fq, sort=sort, rows=100)
        return list(connection.results)
