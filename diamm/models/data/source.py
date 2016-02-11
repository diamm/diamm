from django.db import models
from django.conf import settings
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
    cover_image_url = models.URLField(blank=True, null=True, help_text="""A IIIF Image URL to the cover image used for the source view""")

    format = models.CharField(max_length=255, blank=True, null=True)
    measurements = models.CharField(max_length=512, blank=True, null=True)
    public = models.BooleanField(default=False, help_text="Source Description is Public")
    public_images = models.BooleanField(default=False, help_text="Source Images are Public")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # copyists = models.ManyToManyField("diamm_data.Person",
    #                                   through="diamm_data.SourceCopyist",
    #                                   related_name="sources_copied")

    bibliography = models.ManyToManyField("diamm_data.Bibliography",
                                          through="diamm_data.SourceBibliography")

    # people = models.ManyToManyField("diamm_data.Person",
    #                                 through="diamm_data.SourcePerson",
    #                                 related_name="related_sources")

    # inventory = models.ManyToManyField("diamm_data.Composition",
    #                                    through="diamm_data.Item")

    # provenance = models.ManyToManyField("diamm_data.GeographicArea",
    #                                     through="diamm_data.SourceProvenance",
    #                                     through_fields=("source", "country"),
    #                                     related_name="sources")

    # This will be updated automatically whenever a new source is added.
    # Since databases don't do natural sort and instead default to ASCII sort
    # this will store the current alphanumeric sort order for all of the MSS
    # allowing them to be sorted. As a bonus, it can be coupled with other sort
    # options, e.g., `ordering = ['archive__archivename', 'sort_order']` would sort
    # first by archive, and then by alphanumeric shelf mark.
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
    def composers(self):
        composer_names = []
        for item in self.inventory.all():
            if not item.composition:
                if item.aggregate_composer:
                    composer_names.append(item.aggregate_composer.full_name)
                    continue

            if item.composition:
                for composer in item.composition.composers.all():
                    composer_names.append(composer.composer_name)
        return list(set(composer_names))

    @property
    def compositions(self):
        composition_names = []
        for item in self.inventory.all():
            if not item.composition:
                continue
            composition_names.append(item.composition.name)
        return list(set(composition_names))

    # Fetches results for a source from Solr. Much quicker than hitting up postgres
    # and sorts correctly too!
    @property
    def solr_inventory(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:item', 'source_i:{0}'.format(self.pk)]
        # Set rows to an extremely high number so we get all of the item records in one go.
        item_results = connection.search("*:*", fq=fq, sort="folio_start_ans asc", rows=10000)
        if item_results.docs:
            return item_results.docs
        else:
            return []

    @property
    def solr_bibliography(self):
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ['type:bibliography', 'source_i:{0}'.format(self.pk)]
        bibliography_results = connection.search("*:*", fq=fq, sort="", rows=10000)
        if bibliography_results.docs:
            return bibliography_results.docs
        else:
            return []



