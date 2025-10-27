from django.db import models


class Bibliography(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name = "Bibliography entry"
        verbose_name_plural = "Bibliography entries"
        ordering = ("created",)

    title = models.CharField(max_length=1024)
    # authors = models.ManyToManyField("diamm_data.BibliographyAuthorRole")
    year = models.CharField(max_length=256, blank=True, null=True)
    type = models.ForeignKey("diamm_data.BibliographyType", on_delete=models.CASCADE)
    abbreviation = models.CharField(max_length=128, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        authors = self.authors.all()
        if not authors:
            aut = "[No Author]"
        elif len(authors) > 2:
            authlist = "; ".join([str(a) for a in authors[:2]])
            aut = f"{authlist} et al: "
        else:
            authlist = ", ".join([a.bibliography_author.full_name for a in authors])
            aut = f"{authlist}: "

        return f"{aut}{self.title}"
