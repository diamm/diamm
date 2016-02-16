from django.db import models


class Page(models.Model):
    """
        Represents an object that relates images and items in a source.
        :> Sources have pages, (many) items point to (many) pages, (many) images point to a page.
    """
    class Meta:
        app_label = "diamm_data"
        ordering = ["source__shelfmark", "numeration"]

    source = models.ForeignKey("diamm_data.Source",
                               related_name="pages")

    numeration = models.CharField(max_length=64, help_text="""The folio or page number. If there are many different systems in use,
                                                           choose one and put the others in the note field.""")
    legacy_id = models.CharField(max_length=64, blank=True, null=True)

    # This may be refactored to allow for multiple page sort orders, but for now we'll stick with one
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return "{0}".format(self.numeration)

    @property
    def public_images(self):
        return self.images.filter(public=True)
