from django.db import models


class Image(models.Model):
    class Meta:
        app_label = "diamm_data"

    # item = models.ForeignKey("diamm_data.Item", blank=True, null=True)
    # items = models.ManyToManyField("diamm_data.Item",
    #                                related_name="images")
    #

    page = models.ForeignKey(
        "diamm_data.Page",
        blank=True,
        null=True,
        related_name="images",
        on_delete=models.CASCADE,
    )
    type = models.ForeignKey(
        "diamm_data.ImageType",
        blank=True,
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )
    location = models.URLField(max_length=1024, blank=True, null=True)

    # folio = models.CharField(max_length=256, blank=True, null=True)
    # caption = models.TextField(blank=True, null=True)
    # serial = models.IntegerField(blank=True, null=True)
    legacy_id = models.CharField(max_length=256, blank=True, null=True)
    legacy_filename = models.CharField(max_length=1024, blank=True, null=True)

    iiif_response_cache = models.TextField(
        blank=True, null=True, verbose_name="IIIF Image Response"
    )
    public = models.BooleanField(default=False)
    external = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.location}"
