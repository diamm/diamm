from django.db import models
from diamm.helpers.identifiers import IDENTIFIER_TYPES, TYPE_PREFIX


class SourceAuthority(models.Model):
    """
    Modelled after the "Person" and "Archive" Identifier models. However, the "Source Identifier"
    name was already taken, so this is called a "Source Authority."
    """
    class Meta:
        app_label = "diamm_data"
        verbose_name_plural = "Source authorities"

    identifier = models.CharField(max_length=512, help_text="Do not provide the full URL here; only the identifier.")
    identifier_type = models.IntegerField(choices=IDENTIFIER_TYPES)
    source = models.ForeignKey("diamm_data.Source",
                               related_name="authorities",
                               on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.identifier_label}:{self.identifier}"

    @property
    def identifier_label(self):
        d = dict(IDENTIFIER_TYPES)
        return d[self.identifier_type]

    @property
    def identifier_prefix(self) -> str:
        (pfx, url) = TYPE_PREFIX[self.identifier_type]
        return pfx

    @property
    def identifier_url(self) -> str:
        (pfx, url) = TYPE_PREFIX[self.identifier_type]
        return f"{url}{self.identifier}"
