from django.db import models


class PersonNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    BIOGRAPHY = 1
    VARIANT_NAME_NOTE = 2
    DATE_NOTE = 3
    BIBLIOGRAPHY_NOTE = 4

    NOTE_TYPES = (
        (BIOGRAPHY, "Biography"),
        (VARIANT_NAME_NOTE, "Variant Name"),
        (DATE_NOTE, "Date"),
        (BIBLIOGRAPHY_NOTE, "Bibliography"),
    )

    note = models.TextField()
    type = models.IntegerField(choices=NOTE_TYPES)
    public = models.BooleanField(default=True)
    person = models.ForeignKey(
        "diamm_data.Person", related_name="notes", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.full_name} ({self.note_type})"

    @property
    def note_type(self) -> str:
        d = dict(self.NOTE_TYPES)
        return d[self.type]
