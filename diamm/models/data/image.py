from django.db import models


class Image(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ["filename",]

    # item = models.ForeignKey("diamm_data.Item", blank=True, null=True)
    items = models.ManyToManyField("diamm_data.Item",
                                   related_name="images")

    type = models.ForeignKey("diamm_data.ImageType", blank=True, null=True)
    filename = models.CharField(max_length=1024, blank=True, null=True)
    folio = models.CharField(max_length=256, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    photographer = models.CharField(max_length=512, blank=True, null=True)
    exif = models.TextField(blank=True, null=True)  # future use
    serial = models.IntegerField(blank=True, null=True)
    conditions = models.ManyToManyField("diamm_data.ImagePageCondition")
    legacy_id = models.CharField(max_length=256, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.filename:
            return "{0}".format(self.filename)
        else:
            return "{0}".format(self.folio)

    @property
    def digitized(self):
        """
        :return: True if the filename is set (i.e., an image is attached); False otherwise.
        """
        return self.filename is not None

    @property
    def sources(self):
        """
         Casting to a set eliminates any duplicate source shelfmarks.
        """
        sources = set([i.source.shelfmark for i in self.items.all()])
        return " ".join(sources)
