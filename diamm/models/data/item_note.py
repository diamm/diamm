from django.db import models


class ItemNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    I_GENERAL_NOTE = 1
    I_COPYING_STYLE = 2
    I_CONCORDANCES = 3
    I_DECORATION_COLOUR = 4
    I_DECORATION_STYLE = 5
    I_INITIAL = 6
    I_INITIAL_COLOUR = 7

    # higher numbers are for legacy notes, not to be used going forward
    I_LEGACY_LAYOUT = 50
    I_LEGACY_VOICES = 51
    I_LEGACY_COMPOSITION = 52

    NOTE_TYPE = (
        ("Current", (
         (I_GENERAL_NOTE, "General Note"),
         (I_COPYING_STYLE, "Copying Style"),
         (I_CONCORDANCES, "Concordances"),
         (I_DECORATION_COLOUR, "Decoration Colour"),
         (I_DECORATION_STYLE, "Decoration Style"),
         (I_INITIAL, "Decorated Initial"),
         (I_INITIAL_COLOUR, "Decorated Initial Colour")
        ),),
        ("Legacy", (
         (I_LEGACY_LAYOUT, "Layout"),
         (I_LEGACY_VOICES, "Voices"),
         (I_LEGACY_COMPOSITION, "Aggregate Composition Title")
        ),)
    )

    type = models.IntegerField(choices=NOTE_TYPE)
    note = models.TextField()
    item = models.ForeignKey("diamm_data.Item",
                             related_name="notes")

    @property
    def note_type(self):
        d = dict(self.NOTE_TYPE)
        dc = dict(d['Current'])
        dl = dict(d['Legacy'])
        dc.update(dl)
        return dc[self.type]
