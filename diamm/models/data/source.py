from itertools import groupby
from operator import itemgetter
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
import pysolr


class Source(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ['archive__city__name', 'sort_order']

    HELP_INVENTORY = """Use this checkbox to mark whether DIAMM has provided an inventory for this
    source. Note that if there are items attached to this source they will still appear, but there will be a note on
    the source record stating that DIAMM has not provided an inventory."""

    # enumerate surface types
    PARCHMENT = 1
    PAPER = 2
    VELLUM = 3
    WOOD = 4
    SLATE = 5
    MIXED = 6
    OTHER = 7

    SURFACE_OPTIONS = (
        (PARCHMENT, 'Parchment'),
        (PAPER, 'Paper'),
        (VELLUM, 'Vellum'),
        (WOOD, 'Wood'),
        (SLATE, 'Slate'),
        (MIXED, 'Mixed Paper and Parchment'),
        (OTHER, 'Other')
    )

    id = models.AutoField(primary_key=True)  # migrate old ID
    archive = models.ForeignKey('diamm_data.Archive', related_name="sources")
    name = models.CharField(max_length=255, blank=True, null=True)
    shelfmark = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True, help_text="""A brief description of the source,
                                                                             e.g, 'chant book with added polyphony'""")
    surface = models.IntegerField(choices=SURFACE_OPTIONS, blank=True, null=True)
    inventory_provided = models.BooleanField(default=False, help_text=HELP_INVENTORY)

    start_date = models.IntegerField(blank=True, null=True,
                                     help_text="""Enter the start year as a four digit integer. If
                                     the precise year is not known, enter it rounding DOWN to the closest
                                     decade, and then century. Examples: 1456, 1450, 1400.
                                     """)
    end_date = models.IntegerField(blank=True, null=True,
                                   help_text="""Enter the end year as a four digit integer. If the
                                   precise year is not known, enter it rounding UP to the
                                   closest decade, and then century. Examples: 1456, 1460, 1500.
                                   """)
    date_statement = models.CharField(max_length=512, blank=True, null=True)
    cover_image = models.ForeignKey("diamm_data.Image", blank=True, null=True)
    format = models.CharField(max_length=255, blank=True, null=True)
    measurements = models.CharField(max_length=512, blank=True, null=True)
    public = models.BooleanField(default=False, help_text="Source Description is Public")
    public_images = models.BooleanField(default=False, help_text="Source Images are Public")
    notations = models.ManyToManyField("diamm_data.Notation", blank=True)
    contributions = GenericRelation("diamm_site.Contribution")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    sort_order = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.name:
            return "{0} ({1})".format(self.shelfmark, self.name)
        return "{0}".format(self.shelfmark)

    @property
    def display_name(self):
        return "{0} {1}".format(self.archive.siglum, self.__str__())

    @property
    def surface_type(self):
        if not self.surface:
            return None

        d = dict(self.SURFACE_OPTIONS)
        return d[self.surface]

    @property
    def public_notes(self):
        return self.notes.exclude(type=99)  # exclude private notes

    @property
    def date_notes(self):
        return self.public_notes.filter(type=11)

    @property
    def has_external_images(self):
        """
            Does the source have an external URL pointing to images
            on another website
        """
        # type 4 is the links to external images
        return self.links.filter(type=4).count() > 0

    @property
    def cover(self):
        """
            If a cover image is set, returns the ID for that; else it chooses a random page with an image attached.
        """
        cover_obj = {}
        if self.cover_image:
            cover_obj['id'] = self.cover_image.id
            cover_obj['label'] = self.cover_image.page.numeration
            return cover_obj
        else:
            p = self.pages.order_by("?").only('numeration').first()
            i = p.images.filter(type=1).only('id', 'public').first()
            if i and i.public:
                cover_obj['id'] = i.id
                cover_obj['label'] = p.numeration
                return cover_obj
            else:
                return None

    @property
    def composers(self):
        composer_names = []
        for item in self.inventory.filter(source__id=self.pk).select_related('composition').prefetch_related('unattributed_composers'):
            if not item.composition:
                if item.unattributed_composers.count() > 0:
                    for itcomposer in item.unattributed_composers.all():
                        composer_names.append(itcomposer.composer.full_name)
                    continue
            else:
                for composer in item.composition.composers.all():
                    composer_names.append(composer.composer_name)

        composer_names = list(set(composer_names))
        composer_names.sort()

        return composer_names

    @property
    def num_composers(self):
        c = self.composers
        return len(c)

    @property
    def compositions(self):
        composition_names = []
        for item in self.inventory.all().select_related('composition'):
            if not item.composition:
                continue
            composition_names.append(item.composition.title)
        return list(set(composition_names))

    @property
    def num_compositions(self):
        c = self.compositions
        return len(c)

    # Fetches results for a source from Solr. Much quicker than hitting up postgres
    # and sorts correctly too! Restricting the composition using [* TO *] means that
    # only attributed works are retrieved; see solr_appears_in for retrieving the records
    # where a composer is mentioned but not attached to a composition.
    @property
    def solr_inventory(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:item', 'source_i:{0}'.format(self.pk), 'composition_i:[* TO *]']
        fl = ['bibliography_ii',
              'composers_ssni',
              'composition_i',
              'composition_s',
              'folio_start_s',
              'folio_end_s',
              'num_voices_s',
              'pages_ii',
              'pages_ssni'
              'source_attribution_s',
              'voices_ii',
              'pk']
        # Set rows to an extremely high number so we get all of the item records in one go.
        item_results = connection.search("*:*", fq=fq, fl=fl, sort="folio_start_ans asc", rows=10000)
        if item_results.docs:
            return item_results.docs
        return []

    # Like solr_inventory, but retrieves only inventory items that do not have a composition attached, i.e., composers
    #  that appear in a source but are not attached to a particular one.
    @property
    def solr_uninventoried(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:item', 'source_i:{0}'.format(self.pk), '-composition_i:[* TO *]']
        fl = ['bibliography_ii',
              'composers_ssni',
              'composition_i',
              'composition_s',
              'folio_start_s',
              'folio_end_s',
              'num_voices_s',
              'pages_ii',
              'pages_ssni'
              'source_attribution_s',
              'voices_ii',
              'pk']
        sort = ["composer_ans asc"]
        # Set rows to an extremely high number so we get all of the item records in one go.
        item_results = connection.search("*:*", fq=fq, fl=fl, sort=sort, rows=10000)
        if item_results.docs:
            return item_results.docs
        return []

    @property
    def inventory_by_composer(self):
        """
            inventory: [{
                    composer: Bar, Foo,
                    url: http://foo/bar
                    pieces: [{
                        title: blahblah,
                        url: http://blahblah
                    },etc.]
                }
        """
        inventory = self.solr_inventory

        sortable_inventory = []

        for item in inventory:
            for c in item['composers_ssni']:
                new_item = (c, c.lower(), item)
                sortable_inventory.append(new_item)

        sorted_inventory = sorted(sortable_inventory, key=itemgetter(1))
        grouped_inventory = groupby(sorted_inventory, itemgetter(0))

        output = []
        for namefield, group in grouped_inventory:
            name, pk, uncertain = namefield.split("|")
            obj = {
                "pk": pk,
                "name": name,
                "inventory": []
            }

            if uncertain:
                if uncertain == "True":
                    obj["uncertain"] = True
                else:
                    obj["uncertain"] = False

            for item in group:
                obj["inventory"].append(item[2])

            output.append(obj)
        return output

    @property
    def solr_bibliography(self):
        # Grab a list of the ids for this record
        bibl = self.bibliographies.select_related('bibliography').values_list('bibliography__id', 'primary_study', 'pages', 'notes').order_by('bibliography__authors__bibliography_author__last_name').distinct()
        id_list = ",".join([str(x[0]) for x in bibl])
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:bibliography', "{!terms f=pk}"+id_list]
        bibliography_results = connection.search("*:*", fq=fq, sort="year_ans desc, sort_ans asc", rows=10000)

        if bibliography_results.hits == 0:
            return []

        mapping = {}
        for itm in bibl:
            additional_info = [
                itm[1],      # primary study
                itm[2],      # pages
                itm[3]       # notes
            ]

            mapping[itm[0]] = additional_info

        for res in bibliography_results.docs:
            if res['pk'] in mapping:
                res['primary_study'] = mapping[res['pk']][0]
                res['pages'] = mapping[res['pk']][1]
                res['notes'] = mapping[res['pk']][2]

        return bibliography_results.docs

    @property
    def solr_pages(self):
        # List the pages from their Solr records
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:page', 'source_i:{0}'.format(self.pk)]
        page_results = connection.search("*:*", fq=fq, sort="numeration_ans asc", rows=10000)
        if page_results.docs:
            return page_results.docs
        return []

    @property
    def solr_sets(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:set', 'sources_ii:{0}'.format(self.pk)]
        fl = ["id", "pk", "cluster_shelfmark_s", "sources_ii", "set_type_s"]
        sort = ["shelfmark_ans asc"]

        set_results = connection.search("*:*", fq=fq, fl=fl, sort=sort, rows=10000)

        if set_results.hits > 0:
            return set_results.docs
        return []

    @property
    def solr_provenance(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:sourceprovenance', 'source_i:{0}'.format(self.pk)]
        sort = ['earliest_year_i asc', 'country_s asc']

        provenance_results = connection.search("*:*", fq=fq, sort=sort, rows=10000)

        if provenance_results.hits > 0:
            return provenance_results.docs
        return []

    @property
    def solr_relationships(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:sourcerelationship', 'source_i:{0}'.format(self.pk)]
        rel_results = connection.search("*:*", fq=fq, rows=10000)

        if rel_results.hits > 0:
            return rel_results.docs
        return []

    @property
    def solr_copyists(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:sourcecopyist', 'source_i:{0}'.format(self.pk)]
        copyist_results = connection.search("*:*", fq=fq, rows=10000)

        if copyist_results.hits > 0:
            return copyist_results.docs
        return []
