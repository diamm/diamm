from django.db import models


class ItemNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    GENERAL_NOTE = 1
    COPYING_STYLE = 2
    CONCORDANCES = 3
    LAYOUT = 4
    POSITION = 5
    NON_MUSIC_CONTENTS = 6
    INDEX = 7

    NOTE_TYPE = (
        (GENERAL_NOTE, "General Note"),
        (COPYING_STYLE, "Copying Style"),
        (CONCORDANCES, "Concordances"),
        (LAYOUT, "Layout"),
        (POSITION, "Position on Page"),
        (NON_MUSIC_CONTENTS, "Non-music contents description"),
        (INDEX, "Indexing or Ordering")
    )

    type = models.IntegerField(choices=NOTE_TYPE)
    note = models.TextField()
    item = models.ForeignKey("diamm_data.Item",
                             related_name="notes",
                             on_delete=models.CASCADE)

    @property
    def note_type(self):
        if not self.type:
            return None
        d = dict(self.NOTE_TYPE)
        return d[self.type]
