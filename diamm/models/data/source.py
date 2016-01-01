from django.db import models
from simple_history.models import HistoricalRecords

# enumerate surface types
PARCHMENT = 1
PAPER = 2
VELLUM = 3
WOOD = 4
SLATE = 5
MIXED = 6
OTHER = 7


class Source(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ['archive__city__name', 'sort_order']

    SURFACE_OPTIONS = (
        (1, 'Parchment'),
        (2, 'Paper'),
        (3, 'Vellum'),
        (4, 'Wood'),
        (5, 'Slate'),
        (6, 'Mixed Paper and Parchment'),
    )

    id = models.AutoField(primary_key=True)  # migrate old ID
    archive = models.ForeignKey('diamm_data.Archive', related_name="sources")
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    surface = models.IntegerField(choices=SURFACE_OPTIONS, blank=True, null=True)
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

    format = models.CharField(max_length=255, blank=True, null=True)
    measurements = models.CharField(max_length=512, blank=True, null=True)
    public = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    copyists = models.ManyToManyField("diamm_data.Person",
                                      through="diamm_data.SourceCopyist")

    bibliography = models.ManyToManyField("diamm_data.Bibliography",
                                          through="diamm_data.SourceBibliography")

    # This will be updated automatically whenever a new source is added.
    # Since databases don't do natural sort and instead default to ASCII sort
    # this will store the current alphanumeric sort order for all of the MSS
    # allowing them to be sorted. As a bonus, it can be coupled with other sort
    # options, e.g., `ordering = ['archive__archivename', 'sort_order']` would sort
    # first by archive, and then by alphanumeric shelf mark.
    sort_order = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "{0}".format(self.name)
