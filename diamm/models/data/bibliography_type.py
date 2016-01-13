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

    name = models.CharField(max_length=512)

    def __str__(self):
        return "{0}".format(self.name)
