from django.db import models


class ArchiveNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    PRIVATE = 1
    OTHER_NAMES = 2

    NOTE_TYPES = (
        (PRIVATE, 'Private'),
        (OTHER_NAMES, 'Other Names')
    )

    type = models.IntegerField(choices=NOTE_TYPES)
    note = models.TextField()
    archive = models.ForeignKey("diamm_data.Archive",
                               related_name="notes")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
