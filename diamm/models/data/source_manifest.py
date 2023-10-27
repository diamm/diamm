from django.db import models


class SourceManifest(models.Model):
    class Meta:
        app_label = "diamm_data"

    MANIFEST_VERSION = (
        (2, "v2"),
        (3, "v3")
    )

    source = models.ForeignKey("diamm_data.Source",
                               related_name="manifests",
                               on_delete=models.CASCADE)
    manifest_url = models.CharField(max_length=1024)
    iiif_version = models.IntegerField(choices=MANIFEST_VERSION)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source}"
