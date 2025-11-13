from django.db import models


class PageTypeChoices(models.IntegerChoices):
    PAGE = 1, "Page"
    ENDPAPER_MODERN = 2, "Modern Endpapers"
    ENDPAPER_CONTEMPORARY = 3, "Contemporary Endpapers"
    FLYLEAF = 4, "Flyleaf"
    OPENING = 5, "Opening"
    BINDINGS = 6, "Bindings"
    FRAGMENT = 7, "Fragment(s)"
    SCROLL = 8, "Scroll"
    ADDITIONAL = 9, "Additional"
    SECONDARY = 10, "Pastedown"
    PASTEDOWN = 11, "Offset"
    OFFSET = 12, "Secondary"


class Page(models.Model):
    """
    Represents an object that relates images and items in a source.
    :> Sources have pages, (many) items point to (many) pages, (many) images point to a page.
    """

    class Meta:
        app_label = "diamm_data"
        ordering = ["source__shelfmark", "sort_order"]

    source = models.ForeignKey(
        "diamm_data.Source", related_name="pages", on_delete=models.CASCADE
    )

    numeration = models.CharField(
        max_length=64,
        help_text="""The folio or page number. If there are many different systems in use,
                                                           choose one and put the others in the note field.""",
    )
    # legacy id for the Image it was derived from.
    legacy_id = models.CharField(max_length=64, blank=True, null=True)

    # This may be refactored to allow for multiple page sort orders, but for now we'll stick with one
    sort_order = models.DecimalField(
        default=0, blank=True, null=True, decimal_places=3, max_digits=100
    )
    page_type = models.IntegerField(
        choices=PageTypeChoices.choices,
        default=PageTypeChoices.PAGE,
        blank=True,
        null=True,
    )
    iiif_canvas_uri = models.CharField(max_length=1024, blank=True, null=True)
    external = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.numeration}"

    @property
    def public_images(self):
        return self.images.filter(public=True)

    @property
    def page_kind(self):
        if not self.page_type:
            return None

        d = dict(PageTypeChoices.choices)
        return d[self.page_type]
