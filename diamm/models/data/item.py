from django.db import models


class Item(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("folio_start",)

    L_SCORE = 1
    L_PARTS = 2

    LAYOUT_OPTIONS = (
        (L_SCORE, "Score"),
        (L_PARTS, "Parts")
    )

    source = models.ForeignKey('diamm_data.Source',
                               related_name="inventory")

    pages = models.ManyToManyField("diamm_data.Page",
                                   related_name="items",
                                   blank=True)

    composition = models.ForeignKey("diamm_data.Composition",
                                    related_name="sources",
                                    blank=True,
                                    null=True)

    source_attribution = models.CharField(max_length=1024,
                                          blank=True,
                                          null=True,
                                          help_text="The attribution in the source")
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
    source_order = models.IntegerField(blank=True, null=True)
    page_order = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.composition:
            return "{0}".format(self.composition.title)
        else:
            return "Works in {0}".format(self.source.display_name)

    @property
    def item_type(self):
        if not self.layout:
            return None
        d = dict(self.LAYOUT_OPTIONS)
        return d[self.layout]

