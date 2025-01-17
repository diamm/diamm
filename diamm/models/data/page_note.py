from django.db import models


class PageNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    DECORATION_COLOUR = 1
    DECORATION_STYLE = 2
    INITIAL = 3
    INITIAL_COLOUR = 4

    NOTE_TYPE = (
        (DECORATION_COLOUR, "Decoration Colour"),
        (DECORATION_STYLE, "Decoration Style"),
        (INITIAL, "Decorated Initial"),
        (INITIAL_COLOUR, "Decorated Initial Colour"),
    )

    type = models.IntegerField(choices=NOTE_TYPE)
    note = models.TextField()
    page = models.ForeignKey(
        "diamm_data.Page", related_name="notes", on_delete=models.CASCADE
    )

    @property
    def note_type(self):
        if not self.type:
            return None
        d = dict(self.NOTE_TYPE)
        return d[self.type]
