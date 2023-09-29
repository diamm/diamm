from django.db import models
from diamm.helpers.identifiers import IDENTIFIER_TYPES, TYPE_PREFIX


class OrganizationIdentifier(models.Model):
    class Meta:
        app_label = "diamm_data"

    identifier = models.CharField(max_length=512, help_text="Do not provide the full URL here; only the identifier.")
    identifier_type = models.IntegerField(choices=IDENTIFIER_TYPES)
    organization = models.ForeignKey("diamm_data.Organization",
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

    @property
    def identifier_prefix(self) -> str:
        (pfx, url) = TYPE_PREFIX[self.identifier_type]
        return pfx

    @property
    def identifier_url(self) -> str:
        (pfx, url) = TYPE_PREFIX[self.identifier_type]
        return f"{url}{self.identifier}"
