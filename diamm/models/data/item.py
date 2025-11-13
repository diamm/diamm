from django.db import models

from diamm.helpers.storage import OverwriteStorage


class LayoutOptionsChoices(models.IntegerChoices):
    L_SCORE = 1, "Score"
    L_PARTS = 2, "Parts"


class CompletenessOptionsChoices(models.IntegerChoices):
    C_TEXT_ONLY = 1, "Text only"
    C_MUSIC_ONLY = 2, "Music only"
    C_MISSING_INDEX_ONLY = 3, "Missing; mentioned in index"
    C_CATCHWORD_ONLY = 4, "Catchword only"


class Item(models.Model):
    ITEM_TITLE_HELP = """A title for this item record, ONLY if it is NOT linked to a composition. This is for
                         supplying a name to otherwise untitled things (e.g., "blank page") or
                         for non-musical titles ("A Poem").

                         Use the Source Incipit field to record variant titles for compositions.
                 """

    class Meta:
        app_label = "diamm_data"
        ordering = ("source_order", "folio_start")

    source = models.ForeignKey(
        "diamm_data.Source", related_name="inventory", on_delete=models.CASCADE
    )

    pages = models.ManyToManyField("diamm_data.Page", related_name="items", blank=True)
    external_pages = models.ManyToManyField(
        "diamm_data.ExternalPage",
        related_name="external_items",
        blank=True,
        help_text="Only use with an external IIIF manifest. Use the 'pages' field for all other sources.",
    )

    composition = models.ForeignKey(
        "diamm_data.Composition",
        related_name="sources",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    source_attribution = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="The attribution in the source",
    )

    item_title = models.CharField(
        max_length=1024, blank=True, null=True, help_text=ITEM_TITLE_HELP
    )

    source_incipit = models.TextField(
        blank=True,
        null=True,
        help_text="The incipit or title of the piece given in the source",
    )
    layout = models.IntegerField(
        choices=LayoutOptionsChoices.choices,
        blank=True,
        null=True,
        help_text="Arrangement of pieces on the page",
    )
    folio_start = models.CharField(max_length=256, blank=True, null=True)
    folio_end = models.CharField(max_length=256, blank=True, null=True)
    num_voices = models.CharField(max_length=32, blank=True, null=True)

    position_ms = models.FloatField(blank=True, null=True)
    source_order = models.DecimalField(
        blank=True, null=True, decimal_places=3, max_digits=100
    )
    page_order = models.IntegerField(default=0, blank=True, null=True)

    incipit = models.FileField(
        upload_to="rism/incipits/", storage=OverwriteStorage(), blank=True, null=True
    )

    legacy_composition = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="Used only to record a composition that has been converted to an item-only record",
    )
    notation = models.ForeignKey(
        "diamm_data.Notation", blank=True, null=True, on_delete=models.CASCADE
    )
    fragment = models.BooleanField(
        default=False,
        help_text="""Whether the item represents a fragment of the composition. Only used when
the composition is missing due to physical damage to the MS; do not use for partially-written compositions, compositions
missing voices, or compositions that contain only text or only music.""",
    )

    completeness = models.IntegerField(
        choices=CompletenessOptionsChoices.choices,
        blank=True,
        null=True,
        help_text="""Indicates the completeness of the written composition in the source. Used when the
composition is nominally "whole" within the source, but presents an incomplete view of the composition.""",
    )

    bibliography_json = models.JSONField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.composition:
            return f"{self.composition.title}"
        elif self.item_title:
            return f"{self.item_title}"
        else:
            return f"Works in {self.source.display_name}"

    @property
    def item_type(self):
        if not self.layout:
            return None
        d = dict(LayoutOptionsChoices.choices)
        return d[self.layout]

    @property
    def item_completeness(self) -> str | None:
        if not self.completeness:
            return None

        d = dict(CompletenessOptionsChoices.choices)
        return d[self.completeness]
