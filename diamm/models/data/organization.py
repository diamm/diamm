from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
import pysolr


class Organization(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('name',)

    ARCHIVE_HELP_TEXT = """
        If an organization has an equivalent entry in the Organizations table,
        enter it here and the two will be linked.
    """

    name = models.CharField(max_length=1024, default="s.n.")
    variant_names = models.CharField(max_length=1024, blank=True, null=True)
    type = models.ForeignKey("diamm_data.OrganizationType", default=1)
    legacy_id = models.CharField(max_length=64, blank=True, null=True)
    location = models.ForeignKey("diamm_data.GeographicArea", blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    archive = models.ForeignKey("diamm_data.Archive", blank=True, null=True, help_text=ARCHIVE_HELP_TEXT)

    sources_copied = GenericRelation("diamm_data.SourceCopyist")
    sources_related = GenericRelation("diamm_data.SourceRelationship")
    sources_provenance = GenericRelation("diamm_data.SourceProvenance")
    contributions = GenericRelation("diamm_site.Contribution")

    def __str__(self):
        return "{0}".format(self.name)

    @property
    def solr_copyist(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:sourcecopyist',
              'copyist_type_s:organization',
              'copyist_pk_i:{0}'.format(self.pk)]
        sort = ["source_ans asc"]
        copy_res = connection.search("*:*", fq=fq, sort=sort, rows=10000)

        if copy_res.hits > 0:
            return copy_res.docs
        else:
            return []

    @property
    def solr_relationships(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:sourcerelationship',
              'related_entity_type_s:organization',
              'related_entity_pk_i:{0}'.format(self.pk)]
        sort = ["source_ans asc"]
        rel_res = connection.search("*:*", fq=fq, sort=sort, rows=10000)
        if rel_res.hits > 0:
            return rel_res.docs
        else:
            return []

    @property
    def solr_provenance(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:sourceprovenance',
              'entity_type_s:organization',
              'entity_pk_i:{0}'.format(self.pk)]
        sort = ["source_ans asc"]
        prov_res = connection.search("*:*", fq=fq, sort=sort, rows=10000)

        if prov_res.hits > 0:
            return prov_res.docs
        else:
            return []
