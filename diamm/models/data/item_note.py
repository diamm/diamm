from django.db import models


class ItemNoteTypeChoices(models.IntegerChoices):
    GENERAL_NOTE = 1, "General Note"
    COPYING_STYLE = 2, "Copying Style"
    CONCORDANCES = 3, "Concordances"
    LAYOUT = 4, "Layout"
    POSITION = 5, "Position on Page"
    NON_MUSIC_CONTENTS = 6, "Non-music contents description"
    INDEX = 7, "Indexing or Ordering"
    PHYSICAL = 8, "Physical description (Condition, Legibility, etc.)"
    INTERNAL = 99, "Internal Note"


class ItemNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    type = models.IntegerField(choices=ItemNoteTypeChoices.choices)
    note = models.TextField()
    item = models.ForeignKey(
        "diamm_data.Item", related_name="notes", on_delete=models.CASCADE
    )

    @property
    def note_type(self) -> str | None:
        if not self.type:
            return None
        d = dict(ItemNoteTypeChoices.choices)
        return d[self.type]
