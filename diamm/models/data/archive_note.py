from django.db import models


class ArchiveNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    PRIVATE = 1

    NOTE_TYPES = (
        (PRIVATE, 'Private'),
    )

    type = models.IntegerField(choices=NOTE_TYPES)
    note = models.TextField()
    archive = models.ForeignKey("diamm_data.Archive",
                               related_name="notes")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
