from django.db import models


class CompositionNote(models.Model):
    ALTERNATE_TITLE = 1
    PARS = 2
    GENERAL_NOTE = 3
    ATTRIBUTION_NOTE = 4
    CONTRAFACT_NOTE = 5
    INTABULATION_NOTE = 6

    NOTE_TYPES = (
        (ALTERNATE_TITLE, "Alternate Title"),
        (PARS, "Pars"),
        (GENERAL_NOTE, "General Note"),
        (ATTRIBUTION_NOTE, "Attribution Note"),
        (CONTRAFACT_NOTE, "Contrafact Note"),
        (INTABULATION_NOTE, "Intabulation Note"),
    )

    class Meta:
        app_label = "diamm_data"

    type = models.IntegerField(choices=NOTE_TYPES)
    note = models.TextField()
    composition = models.ForeignKey(
        "diamm_data.Composition", related_name="notes", on_delete=models.CASCADE
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.note_type}: {self.composition.title}"

    @property
    def note_type(self):
        d = dict(self.NOTE_TYPES)
        return d[self.type]
