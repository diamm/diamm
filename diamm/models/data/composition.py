from django.db import models


class Composition(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('name',)

    name = models.CharField(max_length=1024)
    legacy_genre = models.CharField(max_length=512, blank=True, null=True,
                                    help_text="Stores the legacy value for the genre field.")
    anonymous = models.BooleanField(default=False)
    genres = models.ManyToManyField("diamm_data.Genre")

    # composers = models.ManyToManyField("diamm_data.Person",
    #                                    through="diamm_data.CompositionComposer",
    #                                    related_name="compositions")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}".format(self.name)

    @property
    def composer_names(self):
        composers = self.composers.all()
        return "; ".join([c.composer.full_name for c in composers])
