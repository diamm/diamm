from django.db import models


class SourceURL(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name = "Source URL"
        verbose_name_plural = "Source URLs"

    IIIF_MANIFEST = 1
    HOST = 2
    ANCILLARY = 3

    URL_TYPES = (
        (IIIF_MANIFEST, 'IIIF'),
        (HOST, 'Host Institution'),
        (ANCILLARY, 'Ancillary')
    )

    type = models.IntegerField(choices=URL_TYPES)
    link_text = models.CharField(max_length=1024, blank=True, null=True)
    link = models.CharField(max_length=1024)
    source = models.ForeignKey("diamm_data.Source")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}".format(self.link_text)
