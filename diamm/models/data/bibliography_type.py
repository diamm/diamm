from django.db import models


class BibliographyType(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ('name',)

    # These refer to the PKs for each type. They are loaded in the old-to-new DIAMM migration process.
    JOURNAL_ARTICLE = 1
    BOOK = 2
    CHAPTER_IN_BOOK = 3
    DISSERTATION = 4
    FESTSCHRIFT = 5
    JOURNAL = 6
    FACSIMILE = 7
    FACSIMILE_WITH_INTRODUCTION = 8
    EDITION = 9
    LETTER = 10
    REVIEW = 11

    name = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.name}"
