from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from diamm.helpers.solr_helpers import SolrManager


class Person(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name_plural = "People"
        ordering = ["last_name", "first_name"]

    last_name = models.CharField(max_length=512,
                                 help_text="Last name, or full name if it does not follow convention, e.g., 'Louis of Bavaria'")
    first_name = models.CharField(max_length=512, blank=True, null=True)
    title = models.CharField(max_length=512, blank=True, null=True,
                             help_text="Personal title, e.g., Duke, Count, Pope.")
    earliest_year = models.IntegerField(blank=True, null=True)
    earliest_year_approximate = models.BooleanField(default=False)
    latest_year = models.IntegerField(blank=True, null=True)
    latest_year_approximate = models.BooleanField(default=False)

    legacy_id = models.CharField(max_length=64, blank=True, null=True)
    # roles = models.ManyToManyField("diamm_data.Role",
    #                                through="diamm_data.PersonRole")

    sources_copied = GenericRelation("diamm_data.SourceCopyist")
    sources_related = GenericRelation("diamm_data.SourceRelationship")
    sources_provenance = GenericRelation("diamm_data.SourceProvenance")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
        name_str = ""
        if self.first_name:
            name_str = "{0}, {1}".format(self.last_name, self.first_name)
        else:
            name_str = "{0}".format(self.last_name)

        if date_str:
            return "{0} ({1})".format(name_str, date_str)
        else:
            return name_str

    @property
    def full_name(self):
        return self.__str__()

    @property
    def solr_relationships(self):
        connection = SolrManager(settings.SOLR['SERVER'])
        fq = ['type:sourcerelationship', 'related_entity_type_s:person', 'related_entity_pk_i:{0}'.format(self.pk)]
        sort = "source_ans asc"

        connection.search("*:*", fq=fq, sort=sort, rows=100)
        return list(connection.results)

    @property
    def solr_copyist(self):
        connection = SolrManager(settings.SOLR['SERVER'])
        fq = ['type:sourcecopyist', 'copyist_type_s:person', 'copyist_pk_i:{0}'.format(self.pk)]
        sort = "source_ans asc"

        connection.search("*:*", fq=fq, sort=sort, rows=100)
        return list(connection.results)

    @property
    def solr_compositions(self):
        connection = SolrManager(settings.SOLR['SERVER'])
        uncertain_ids = self.compositions.filter(uncertain=True).values_list('composition__pk', flat=True)
        fq = ['type:composition', 'composers_ii:{0}'.format(self.pk)]
        sort = "title_s asc"
        connection.search("*:*", fq=fq, sort=sort, rows=100)

        reslist = []
        if connection.hits > 0:
            for res in connection.results:
                if res['pk'] in uncertain_ids:
                    res['uncertain'] = True
                else:
                    res['uncertain'] = False
                reslist.append(res)

        return reslist
