from django.db import models


class Composition(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('title',)

    title = models.CharField(max_length=1024)
    legacy_genre = models.CharField(max_length=512, blank=True, null=True,
                                    help_text="Stores the legacy value for the genre field.")
    anonymous = models.BooleanField(default=False)
    genres = models.ManyToManyField("diamm_data.Genre", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

    @property
    def composer_names(self):
        composers = self.composers.select_related('composer', 'composition').all()
        return "; ".join([c.composer_name for c in composers])
