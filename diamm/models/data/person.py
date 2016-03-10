from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
import pysolr


class Person(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name_plural = "People"
        ordering = ["last_name", "first_name"]

    last_name = models.CharField(max_length=512,
                                 help_text="Last name, or full name if it does not follow modern conventions, e.g., 'Louis of Bavaria'")
    first_name = models.CharField(max_length=512, blank=True, null=True)
    title = models.CharField(max_length=512, blank=True, null=True,
                             help_text="Personal title, e.g., Duke, Count, Pope.")
    earliest_year = models.IntegerField(blank=True, null=True)
    earliest_year_approximate = models.BooleanField(default=False)
    latest_year = models.IntegerField(blank=True, null=True)
    latest_year_approximate = models.BooleanField(default=False)

    legacy_id = models.CharField(max_length=64)
    roles = models.ManyToManyField("diamm_data.Role",
                                   through="diamm_data.PersonRole")

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
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:sourcerelationship', 'related_entity_type_s:person', 'related_entity_pk_i:{0}'.format(self.pk)]
        rel_res = connection.search("*:*", fq=fq, rows=1000)

        if rel_res.hits > 0:
            return rel_res.docs
        else:
            return []
