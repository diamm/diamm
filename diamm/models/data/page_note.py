from django.db import models


class PageNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    GENERAL_NOTE = 1
    COPYING_STYLE = 2
    CONCORDANCES = 3
    DECORATION_COLOUR = 4
    DECORATION_STYLE = 5
    INITIAL = 6
    INITIAL_COLOUR = 7

    # higher numbers are for legacy notes, not to be used going forward
    LEGACY_LAYOUT = 50
    LEGACY_VOICES = 51
    LEGACY_COMPOSITION = 52

    NOTE_TYPE = (
        ("Current", (
         (GENERAL_NOTE, "General Note"),
         (COPYING_STYLE, "Copying Style"),
         (CONCORDANCES, "Concordances"),
         (DECORATION_COLOUR, "Decoration Colour"),
         (DECORATION_STYLE, "Decoration Style"),
         (INITIAL, "Decorated Initial"),
         (INITIAL_COLOUR, "Decorated Initial Colour")
        ),),
        ("Legacy", (
         (LEGACY_LAYOUT, "Layout"),
         (LEGACY_VOICES, "Voices"),
         (LEGACY_COMPOSITION, "Aggregate Composition Title")
        ),)
    )

    type = models.IntegerField(choices=NOTE_TYPE)
    note = models.TextField()
    page = models.ForeignKey("diamm_data.Page",
                             related_name="notes")

    @property
    def note_type(self):
        d = dict(self.NOTE_TYPE)
        dc = dict(d['Current'])
        dl = dict(d['Legacy'])
        dc.update(dl)
        return dc[self.type]
