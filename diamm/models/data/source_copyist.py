from django.db import models


class SourceCopyist(models.Model):
    class Meta:
        app_label = "diamm_data"

    MUSIC_COPYIST = 1
    TEXT_COPYIST = 2
    INDEXER = 3
    LIMINARY_TEXT = 4
    ILLUMINATOR = 5
    TEXT_AND_MUSIC = 6

    SOURCE_COPYIST_TYPES = (
        (MUSIC_COPYIST, "Music"),
        (TEXT_COPYIST, "Text"),
        (INDEXER, "Indexer"),
        (LIMINARY_TEXT, "Liminary Text"),
        (ILLUMINATOR, "Illuminator"),
        (TEXT_AND_MUSIC, "Text and Music")
    )

    source = models.ForeignKey("diamm_data.Source",
                               on_delete=models.CASCADE,
                               related_name="copyists")
    copyist = models.ForeignKey("diamm_data.Person",
                                on_delete=models.CASCADE,
                                related_name="sources_copied")

    uncertain = models.BooleanField(default=False)
    type = models.IntegerField(choices=SOURCE_COPYIST_TYPES, blank=True, null=True)

