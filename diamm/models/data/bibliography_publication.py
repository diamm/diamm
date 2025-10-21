from django.db import models


class BibliographyPublication(models.Model):
    """
    This class stores additional publication info about a bibliography entry.
    It is abstracted here so that these may be "mixed and matched" with
    bibliography entries without needing to assume a set format of entry.

    For example, a Volume or Series Number, normally attached to a Journal
    Article, may occasionally be needed on a published book.
    """

    class Meta:
        app_label = "diamm_data"
        verbose_name = "Additional Publication Info"
        verbose_name_plural = "Additional Publication Info"

    B_VOLUME_NO = 1
    B_PARENT_TITLE = 2
    B_PUBLISHER = 3
    B_PAGES = 4
    B_UNIVERSITY = 5
    B_DEGREE = 6
    B_CHAPTER = 7
    B_SERIES = 8
    B_URL = 9
    B_URL_ACCESSED = 10
    B_TRANSLATOR = 11
    B_FESTSCHRIFT_FOR = 12
    B_PLACE_PUBLICATION = 13
    B_NUMBER_OF_VOLUMES = 14
    B_INTL_NUM = 15
    B_CONFERENCE_NAME = 16
    B_CONFERENCE_LOCATION = 17
    B_CONFERENCE_DATE = 18
    B_NOTE = 99

    PUBLICATION_INFO_TYPE = (
        (B_VOLUME_NO, "Volume (and Issue) Number"),
        (B_PARENT_TITLE, "Title of Parent Entry (i.e., Book title, Journal title)"),
        (B_PUBLISHER, "Publisher"),
        (B_PAGES, "Pages"),
        (B_UNIVERSITY, "University and Department (for Dissertations)"),
        (B_DEGREE, "Degree (for Dissertations)"),
        (B_SERIES, "Series Title (NB: Use Parent Title for journal names)"),
        (B_URL, "URL"),
        (B_URL_ACCESSED, "URL Accessed Date"),
        (B_TRANSLATOR, "Translator Statement"),
        (B_FESTSCHRIFT_FOR, "Festschrift Dedicatee"),
        (B_PLACE_PUBLICATION, "Place of Publication"),
        (B_NUMBER_OF_VOLUMES, "Number of Volumes in Series"),
        (B_INTL_NUM, "ISBN/ISSN/ISMN"),
        (B_CONFERENCE_NAME, "Conference name"),
        (B_CONFERENCE_LOCATION, "Conference location"),
        (B_CONFERENCE_DATE, "Conference date"),
        (B_NOTE, "General Note"),
    )

    entry = models.CharField(max_length=2048)
    type = models.IntegerField(choices=PUBLICATION_INFO_TYPE)
    bibliography = models.ForeignKey(
        "diamm_data.Bibliography",
        related_name="publication_info",
        on_delete=models.CASCADE,
    )

    @property
    def publication_type(self):
        d = dict(self.PUBLICATION_INFO_TYPE)
        return d[self.type]
