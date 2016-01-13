from django.db import models


class CompositionComposer(models.Model):
    class Meta:
        app_label = "diamm_data"

    composition = models.ForeignKey("diamm_data.Composition",
                                    related_name="composers")

    composer = models.ForeignKey("diamm_data.Person",
                                 related_name="compositions")
    uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    @property
    def composer_name(self):
        return self.composer.full_name
