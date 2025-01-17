from django.db import models


class Set(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("type", "cluster_shelfmark")

    PARTBOOKS = 1
    FRAGMENTS = 2
    LINKED_ORIGINS = 3
    NON_MUSIC = 4
    SCRIBAL = 5
    SEPARATE_VOLUMES = 6
    PROJECT = 7

    SET_TYPES = (
        (PARTBOOKS, "Partbooks"),
        (FRAGMENTS, "Fragments of a whole"),
        (LINKED_ORIGINS, "Linked by Origin or Contents"),
        (NON_MUSIC, "Non-music Collection"),
        (SCRIBAL, "Copyist or Scribal Concordance"),
        (SEPARATE_VOLUMES, "Source bound in separate volumes"),
        (PROJECT, "Project Collection"),
    )

    cluster_shelfmark = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    bibliography = models.ManyToManyField(
        "diamm_data.Bibliography", through="diamm_data.SetBibliography"
    )
    sources = models.ManyToManyField("diamm_data.Source", related_name="sets")
    type = models.IntegerField(choices=SET_TYPES)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cluster_shelfmark

    @property
    def set_type(self):
        d = dict(self.SET_TYPES)
        return d[self.type]
