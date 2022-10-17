from django.db import models
from diamm.helpers.storage import OverwriteStorage


class Item(models.Model):
    ITEM_TITLE_HELP = """A title for this item record, ONLY if it is NOT linked to a composition. This is for
                         supplying a name to otherwise untitled things (e.g., "blank page") or 
                         for non-musical titles ("A Poem").
                         
                         Use the Source Attribution field to record variant titles for compositions.
                 """

    class Meta:
        app_label = "diamm_data"
        ordering = ("source_order", "folio_start")

    L_SCORE = 1
    L_PARTS = 2

    LAYOUT_OPTIONS = (
        (L_SCORE, "Score"),
        (L_PARTS, "Parts")
    )

    source = models.ForeignKey('diamm_data.Source',
                               related_name="inventory",
                               on_delete=models.CASCADE)

    pages = models.ManyToManyField("diamm_data.Page",
                                   related_name="items",
                                   blank=True)

    composition = models.ForeignKey("diamm_data.Composition",
                                    related_name="sources",
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE)

    source_attribution = models.CharField(max_length=1024,
                                          blank=True,
                                          null=True,
                                          help_text="The attribution in the source")

    item_title = models.CharField(max_length=1024,
                                  blank=True,
                                  null=True,
                                  help_text=ITEM_TITLE_HELP)

    source_incipit = models.TextField(blank=True, null=True,
                                      help_text="The incipit in the source")
    layout = models.IntegerField(choices=LAYOUT_OPTIONS,
                                 blank=True,
                                 null=True,
                                 help_text="Arrangement of pieces on the page")
    folio_start = models.CharField(max_length=256, blank=True, null=True)
    folio_end = models.CharField(max_length=256, blank=True, null=True)
    num_voices = models.CharField(max_length=32, blank=True, null=True)

    legacy_position_ms = models.CharField(max_length=256, blank=True, null=True)  # transfer for ordering, but we should be able to find a better way to do this.
    source_order = models.DecimalField(blank=True, null=True, decimal_places=3, max_digits=100)
    page_order = models.IntegerField(default=0, blank=True, null=True)

    incipit = models.FileField(
        upload_to='rism/incipits/',
        storage=OverwriteStorage(),
        blank=True, null=True
    )

    legacy_composition = models.CharField(max_length=32,
                                          blank=True,
                                          null=True,
                                          help_text="Used only to record a composition that has been converted to an item-only record")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.composition:
            return "{0}".format(self.composition.title)
        elif self.item_title:
            return "{0}".format(self.item_title)
        else:
            return "Works in {0}".format(self.source.display_name)

    @property
    def item_type(self):
        if not self.layout:
            return None
        d = dict(self.LAYOUT_OPTIONS)
        return d[self.layout]

