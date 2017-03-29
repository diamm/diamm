from django.db import models


class SourceNote(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('type',)

    GENERAL_NOTE = 1
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
    DECORATION_NOTE = 15
    CONTENTS_NOTE = 16
    SURFACE_NOTE = 17
    DIAMM_NOTE = 18
    RISM_NOTE = 97  # was 2
    CCM_NOTE = 98   # was 3
    PRIVATE_NOTE = 99

    NOTE_TYPES = (
        (GENERAL_NOTE, 'General Description'),
        (RISM_NOTE, 'RISM Description'),
        (CCM_NOTE, 'Census Catalogue of Music Description'),
        (EXTENT_NOTE, 'Extent Note'),
        (PHYSICAL_NOTE, 'Physical Description Note'),
        (BINDING_NOTE, 'Binding Note'),
        (OWNERSHIP_NOTE, 'Ownership Note'),
        (WATERMARK_NOTE, 'Watermark Note'),
        (LIMINARY_NOTE, 'Liminary Note'),
        (NOTATION_NOTE, 'Notation Note'),
        (DATE_NOTE, 'Date Note'),
        (DEDICATION_NOTE, 'Dedication Note'),
        (RULING_NOTE, 'Ruling Note'),
        (FOLIATION_NOTE, 'Foliation Note'),
        (DECORATION_NOTE, 'Decoration Note'),
        (CONTENTS_NOTE, 'Contents Note'),
        (SURFACE_NOTE, 'Surface Note'),
        (DIAMM_NOTE, "DIAMM Note"),
        (PRIVATE_NOTE, 'Private Note')
    )

    type = models.IntegerField(choices=NOTE_TYPES)
    note = models.TextField()
    source = models.ForeignKey("diamm_data.Source",
                               related_name="notes")
    sort = models.IntegerField(default=0)

    # Authority for the note
    author = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}: {1}".format( self.note_type, self.source.display_name)

    @property
    def note_type(self):
        d = dict(self.NOTE_TYPES)
        return d[self.type]
