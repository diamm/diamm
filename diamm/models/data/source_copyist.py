from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SourceCopyist(models.Model):
    class Meta:
        app_label = "diamm_data"

    MUSIC_COPYIST = 1
    TEXT_COPYIST = 2
    INDEXER = 3
    LIMINARY_TEXT = 4
    ILLUMINATOR = 5
    TEXT_AND_MUSIC = 6
    UNKNOWN = 7

    SOURCE_COPYIST_TYPES = (
        (MUSIC_COPYIST, "Music"),
        (TEXT_COPYIST, "Text"),
        (INDEXER, "Indexer"),
        (LIMINARY_TEXT, "Liminary Text"),
        (ILLUMINATOR, "Illuminator"),
        (TEXT_AND_MUSIC, "Text and Music"),
        (UNKNOWN, "Unknown")
    )

    source = models.ForeignKey("diamm_data.Source",
                               on_delete=models.CASCADE,
                               related_name="copyists")

    uncertain = models.BooleanField(default=False)
    type = models.IntegerField(choices=SOURCE_COPYIST_TYPES, blank=True, null=True)

    # Copyists can be either People or Organizations.
    limit = models.Q(app_label='diamm_data', model="person") | models.Q(app_label='diamm_data', model='organization')
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    copyist = GenericForeignKey()

    def __str__(self):
        return f"{self.copyist} ({self.copyist_type})"

    @property
    def copyist_type(self):
        if not self.type:
            return None

        d = dict(self.SOURCE_COPYIST_TYPES)
        return d[self.type]


