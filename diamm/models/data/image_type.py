from django.db import models


class ImageType(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('name',)

    # refers to the PK of the types loaded by the fixtures. See: fixtures/image_file_types.json
    PRIMARY = 1
    COLOUR_UV = 2
    WATERMARK = 3
    DETAIL = 4
    GRAYSCALE_UV = 5
    DIGITALLY_ENHANCED = 6
    LEVEL_ADJUST = 7
    DIGITALLY_RESTORED = 8
    ALT_EXPOSURE = 9
    INFRARED = 10
    ALT_FOCUS = 11
    ALT_SHOT = 12
    RAKING_LIGHT = 13
    TOP_HALF_OF_PAGE = 14

    name = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.name}"
