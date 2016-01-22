from django.db import models


class PersonNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    BIOGRAPHY = 1
    VARIANT_NAME_NOTE = 2
    DATE_NOTE = 3

    NOTE_TYPES = (
        (BIOGRAPHY, "Biography"),
        (VARIANT_NAME_NOTE, "Variant Name"),
        (DATE_NOTE, "Date")
    )

    note = models.TextField()
    type = models.IntegerField(choices=NOTE_TYPES)
    public = models.BooleanField(default=True)
    person = models.ForeignKey('diamm_data.Person',
                               related_name="notes")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
