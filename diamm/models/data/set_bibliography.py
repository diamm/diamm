from django.db import models


class SetBibliography(models.Model):
    class Meta:
        app_label = "diamm_data"
        # ordering = ('bibliography__authors__bibliography_author__last_name',)

    set = models.ForeignKey(
        "diamm_data.Set", related_name="bibliographies", on_delete=models.CASCADE
    )
    bibliography = models.ForeignKey(
        "diamm_data.Bibliography", related_name="sets", on_delete=models.CASCADE
    )

    notes = models.TextField(blank=True, null=True)
    pages = models.TextField(blank=True, null=True)
