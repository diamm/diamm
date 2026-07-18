from django.db import models


class CompositionURLTypeChoices(models.IntegerChoices):
    EDITION = 1, "Edition"
    SCORE = 2, "Score"


class CompositionURL(models.Model):
    class Meta:
        app_label = "diamm_data"
        verbose_name = "Composition URL"
        verbose_name_plural = "Composition URLs"
        ordering = ("type", "pk")

    composition = models.ForeignKey(
        "diamm_data.Composition", related_name="links", on_delete=models.CASCADE
    )
    type = models.IntegerField(choices=CompositionURLTypeChoices.choices)
    link_text = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="A description of the linked edition or score.",
    )
    link = models.URLField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.link_text or self.link

    @property
    def url_type(self):
        return self.get_type_display()
