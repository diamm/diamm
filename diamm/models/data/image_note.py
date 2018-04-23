from django.db import models


class ImageNote(models.Model):
    class Meta:
        app_label = "diamm_data"

    GENERAL = 1
    CAPTURE_CONDITIONS = 2
    CAPTURE_DEVICE = 3
    FOCUS = 4
    GAMMA = 5

    NOTE_TYPE = (
        (GENERAL, "General"),
        (CAPTURE_CONDITIONS, "Capture Conditions"),
        (CAPTURE_DEVICE, "Capture Device")
    )

    type = models.IntegerField(choices=NOTE_TYPE)
    note = models.TextField()
    image = models.ForeignKey("diamm_data.Image",
                              on_delete=models.CASCADE)

