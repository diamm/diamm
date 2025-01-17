from django.db import models
from django.utils.functional import cached_property


class Composition(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("title",)

    title = models.CharField(max_length=1024)
    legacy_genre = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        help_text="Stores the legacy value for the genre field.",
    )
    anonymous = models.BooleanField(default=False)
    genres = models.ManyToManyField("diamm_data.Genre", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

    @cached_property
    def composer_names(self) -> list:
        composers = self.composers.prefetch_related("composer").all()
        cnames = []
        for c in composers:
            cname = c.composer_name
            cattr = "?" if c.uncertain else ""
            cnames.append(f"{cattr}{cname}")
        return cnames
