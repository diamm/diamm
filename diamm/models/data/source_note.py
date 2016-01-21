from django.db import models


class SourceNote(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('type',)

    GENERAL_NOTE = 1
    RISM_NOTE = 2
    CCM_NOTE = 3
    EXTENT_NOTE = 4
    PHYSICAL_NOTE = 5
    BINDING_NOTE = 6
    OWNERSHIP_NOTE = 7
    WATERMARK_NOTE = 8
    LIMINARY_NOTE = 9
    NOTATION_NOTE = 10
    DATE_NOTE = 11
    DEDICATION_NOTE = 12
    RULING_NOTE = 13
    FOLIATION_NOTE = 14
    PRIVATE_NOTE = 99

    NOTE_TYPES = (
        (GENERAL_NOTE, 'General'),
        (RISM_NOTE, 'RISM'),
        (CCM_NOTE, 'CCM'),
        (EXTENT_NOTE, 'Extent'),
        (PHYSICAL_NOTE, 'Physical Description'),
        (BINDING_NOTE, 'Binding'),
        (OWNERSHIP_NOTE, 'Ownership'),
        (WATERMARK_NOTE, 'Watermark'),
        (LIMINARY_NOTE, 'Liminary'),
        (NOTATION_NOTE, 'Notation'),
        (DATE_NOTE, 'Date'),
        (DEDICATION_NOTE, 'Dedication'),
        (RULING_NOTE, 'Ruling'),
        (FOLIATION_NOTE, 'Foliation'),
        (PRIVATE_NOTE, 'Private')
    )

    type = models.IntegerField(choices=NOTE_TYPES)
    note = models.TextField()
    source = models.ForeignKey("diamm_data.Source",
                               related_name="notes")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def note_type(self):
        d = dict(self.NOTE_TYPES)
        return d[self.type]
