from django.db import models

from diamm.helpers.identifiers import IDENTIFIER_TYPES


class ArchiveIdentifier(models.Model):
    class Meta:
        app_label = "diamm_data"

    identifier = models.CharField(max_length=512)
    identifier_type = models.IntegerField(choices=IDENTIFIER_TYPES)
    archive = models.ForeignKey("diamm_data.Archive",
                                related_name="identifiers",
                                on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.identifier_label}:{self.identifier}"

    @property
    def identifier_label(self):
        d = dict(IDENTIFIER_TYPES)
        return d[self.identifier_type]
