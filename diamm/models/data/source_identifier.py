from django.db import models


SHELFMARK = 1
RISM = 2
CCM = 3
EARP = 4
OLIM = 5


class SourceIdentifier(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name = "Source Identifier"

    IDENTIFIER_TYPES = (
        (1, 'Shelfmark'),
        (2, 'RISM'),
        (3, 'CCM'),
        (4, 'EARP'),
        (5, 'olim (Former shelfmark)')
    )

    identifier = models.CharField(max_length=255)
    type = models.IntegerField(choices=IDENTIFIER_TYPES)
    note = models.TextField(blank=True, null=True)
    source = models.ForeignKey("diamm_data.Source",
                               related_name="identifiers")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}".format(self.identifier)
