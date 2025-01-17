from django.conf import settings
from django.db import models

from diamm.helpers.solr_helpers import SolrManager


class BibliographyAuthor(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("last_name", "first_name")

    last_name = models.CharField(max_length=512)
    first_name = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        if self.first_name:
            return f"{self.last_name}, {self.first_name}"
        return f"{self.last_name}"

    @property
    def full_name(self):
        return str(self.__str__())

    @property
    def solr_bibliography(self):
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = ["type:bibliography", f"authors_ii:{self.pk}"]
        sort = "year_ans desc, sort_ans asc"

        connection.search("*:*", fq=fq, sort=sort, rows=100)
        return list(connection.results)
