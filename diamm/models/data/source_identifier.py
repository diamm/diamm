from django.db import models


class SourceIdentifier(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name = "Source Identifier"
        ordering = ('type',)

    RISM = 2
    CCM = 3
    OTHER = 4
    OLIM = 5
    ALTN = 6

    IDENTIFIER_TYPES = (
        (RISM, 'RISM'),
        (CCM, 'CCM'),
        (OTHER, 'Other catalogues/source'),
        (OLIM, 'olim (Former shelfmark)'),
        (ALTN, 'Alternative names')
    )

    identifier = models.CharField(max_length=255)
    type = models.IntegerField(choices=IDENTIFIER_TYPES)
    note = models.TextField(blank=True, null=True)
    source = models.ForeignKey("diamm_data.Source",
                               related_name="identifiers",
                               on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}".format(self.identifier)

    @property
    def identifier_type(self):
        d = dict(self.IDENTIFIER_TYPES)
        return d[self.type]
