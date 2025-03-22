from django.db import models


class Image(models.Model):
    class Meta:
        app_label = "diamm_data"

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
    location = models.CharField(max_length=1024, blank=True, null=True)
    legacy_id = models.CharField(max_length=256, blank=True, null=True)
    legacy_filename = models.CharField(max_length=1024, blank=True, null=True)

    width = models.IntegerField(default=0, blank=True, null=True)
    height = models.IntegerField(default=0, blank=True, null=True)
    public = models.BooleanField(default=False)
    external = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.location}"
