from django.db import models


class Page(models.Model):
    """
        Represents an object that relates images and items in a source.
        :> Sources have pages, (many) items point to (many) pages, (many) images point to a page.
    """
    PAGE = 1
    ENDPAPER_MODERN = 2
    ENDPAPER_CONTEMPORARY = 3
    FLYLEAF = 4
    OPENING = 5
    BINDINGS = 6
    FRAGMENT = 7
    SCROLL = 8
    ADDITIONAL = 9
    SECONDARY = 10
    PASTEDOWN = 11
    OFFSET = 12

    PAGE_TYPE_CHOICES = (
        (PAGE, "Page"),
        (ENDPAPER_MODERN, "Modern Endpapers"),
        (ENDPAPER_CONTEMPORARY, "Contemporary Endpapers"),
        (FLYLEAF, "Flyleaf"),
        (OPENING, "Opening"),
        (BINDINGS, "Bindings"),
        (FRAGMENT, "Fragment(s)"),
        (SCROLL, "Scroll"),
        (ADDITIONAL, "Additional"),
        (PASTEDOWN, "Pastedown"),
        (OFFSET, "Offset"),
        (SECONDARY, "Secondary")
    )

    class Meta:
        app_label = "diamm_data"
        ordering = ["source__shelfmark", "sort_order"]

    source = models.ForeignKey("diamm_data.Source",
                               related_name="pages")

    numeration = models.CharField(max_length=64, help_text="""The folio or page number. If there are many different systems in use,
                                                           choose one and put the others in the note field.""")
    # legacy id for the Image it was derived from.
    legacy_id = models.CharField(max_length=64, blank=True, null=True)

    # This may be refactored to allow for multiple page sort orders, but for now we'll stick with one
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    page_type = models.IntegerField(choices=PAGE_TYPE_CHOICES, default=PAGE, blank=True, null=True)

    def __str__(self):
        return "{0}".format(self.numeration)

    @property
    def public_images(self):
        return self.images.filter(public=True)

    @property
    def page_kind(self):
        if not self.page_type:
            return None

        d = dict(self.PAGE_TYPE_CHOICES)
        return d[self.page_type]
