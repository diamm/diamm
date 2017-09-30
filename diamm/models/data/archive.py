import os
import pysolr
from django.db import models
from django.conf import settings
from diamm.helpers.storage import OverwriteStorage


class Archive(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ['city__name', 'name']

    # IDs from the old database to the new database will be maintained
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=512, default="S.N.")
    city = models.ForeignKey('diamm_data.GeographicArea',
                             related_name="archives", blank=True, null=True)
    siglum = models.CharField(max_length=64, blank=True, null=True)
    librarian = models.CharField(max_length=255, blank=True, null=True)
    secondary_contact = models.CharField(max_length=255, blank=True, null=True)
    former_name = models.CharField(max_length=512, blank=True, null=True)

    address_1 = models.TextField(blank=True, null=True)
    address_2 = models.TextField(blank=True, null=True)
    address_3 = models.TextField(blank=True, null=True)
    address_4 = models.TextField(blank=True, null=True)
    address_5 = models.TextField(blank=True, null=True)
    address_6 = models.TextField(blank=True, null=True)
    address_7 = models.TextField(blank=True, null=True)
    address_8 = models.TextField(blank=True, null=True)
    fax = models.CharField(max_length=128, blank=True, null=True)
    telephone = models.CharField(max_length=128, blank=True, null=True)
    website = models.CharField(max_length=1024, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = models.FileField(
            upload_to='archives/',
            storage=OverwriteStorage(),
            blank=True, null=True
    )
    copyright_statement = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.city:
            return "{0}, {1}".format(self.name, self.city.name)
        return "{0}".format(self.name)

    @property
    def display_name(self):
        return str(self)

    @property
    def public_notes(self):
        return self.notes.exclude(type=1)  # exclude private notes.

    @property
    def solr_sources(self):
        """
            We use this method to return a list of sources for this archive
            sorted by shelfmark. (Solr can do alphanumeric sort but the database
            cannot.
        """
        conn = pysolr.Solr(settings.SOLR['SERVER'])
        q = {
            "fq": ['type:source', 'archive_i:{0}'.format(self.pk)],
            "fl": ["pk",
                   "public_images_b",
                   'display_name_s',
                   'cover_image_i',
                   'source_type_s',
                   'date_statement_s',
                   'surface_type_s'],
            "rows": 10000,
            "sort": ["shelfmark_ans asc"]
        }

        res = conn.search("*:*", **q)
        if res.hits > 0:
            return res.docs
        else:
            return []
