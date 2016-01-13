from django.db import models


class Item(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("source__sort_order", "folio_start")

    L_SCORE = 1
    L_PARTS = 2

    LAYOUT_OPTIONS = (
        (L_SCORE, "Score"),
        (L_PARTS, "Parts")
    )

    AGGREGATE_HELP = """For inventories containing aggregate entries for a composer,
    i.e., 'works by' entries, enter the composer here. (This eliminates the need for relating
    composers to sources through dummy compositions)"""

    source = models.ForeignKey('diamm_data.Source',
                               related_name="inventory")

    composition = models.ForeignKey("diamm_data.Composition",
                                    related_name="sources",
                                    blank=True,
                                    null=True)
    aggregate_composer = models.ForeignKey("diamm_data.Person",
                                           blank=True,
                                           null=True,
                                           help_text=AGGREGATE_HELP)
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
    num_voices = models.IntegerField(blank=True, null=True)

    legacy_position_ms = models.CharField(max_length=256, blank=True, null=True)  # transfer for ordering, but we should be able to find a better way to do this.
    source_order = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if not self.composition:
            return "{0}".format(self.source.shelfmark)
        return "{0} ({1})".format(self.composition.name, self.source.shelfmark)

    @property
    def item_type(self):
        if not self.layout:
            return None
        d = dict(self.LAYOUT_OPTIONS)
        return d[self.layout]

