from django.db import models


class LegacyBibliography(models.Model):
    bibliographykey = models.IntegerField(db_column='bibliographyKey', primary_key=True)  # Field name made lowercase.
    biblabbrev = models.TextField(db_column='biblAbbrev', blank=True, null=True)  # Field name made lowercase.
    author1surname = models.TextField(db_column='Author1Surname', blank=True, null=True)  # Field name made lowercase.
    author1firstname = models.TextField(db_column='Author1Firstname', blank=True, null=True)  # Field name made lowercase.
    booktitle = models.TextField(db_column='bookTitle', blank=True, null=True)  # Field name made lowercase.
    articletitle = models.TextField(db_column='articleTitle', blank=True, null=True)  # Field name made lowercase.
    journal = models.TextField(blank=True, null=True)
    vol = models.TextField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)
    publisher = models.TextField(blank=True, null=True)
    placepublication = models.TextField(db_column='placePublication', blank=True, null=True)  # Field name made lowercase.
    page = models.TextField(blank=True, null=True)
    author2surname = models.TextField(db_column='Author2Surname', blank=True, null=True)  # Field name made lowercase.
    author2firstname = models.TextField(db_column='Author2Firstname', blank=True, null=True)  # Field name made lowercase.
    author3firstname = models.TextField(db_column='Author3Firstname', blank=True, null=True)  # Field name made lowercase.
    author3surname = models.TextField(db_column='Author3Surname', blank=True, null=True)  # Field name made lowercase.
    informationsource = models.TextField(db_column='informationSource', blank=True, null=True)  # Field name made lowercase.
    festschrift = models.TextField(blank=True, null=True)
    editor1surname = models.TextField(db_column='Editor1Surname', blank=True, null=True)  # Field name made lowercase.
    dissertation = models.TextField(blank=True, null=True)
    university = models.TextField(blank=True, null=True)
    degree = models.TextField(blank=True, null=True)
    editor2surname = models.TextField(db_column='Editor2Surname', blank=True, null=True)  # Field name made lowercase.
    editor2firstname = models.TextField(db_column='Editor2Firstname', blank=True, null=True)  # Field name made lowercase.
    editor1firstname = models.TextField(db_column='Editor1Firstname', blank=True, null=True)  # Field name made lowercase.
    seriestitle = models.TextField(db_column='seriesTitle', blank=True, null=True)  # Field name made lowercase.
    volno = models.TextField(db_column='volNo', blank=True, null=True)  # Field name made lowercase.
    chapter = models.TextField(blank=True, null=True)
    editor3surname = models.TextField(db_column='Editor3Surname', blank=True, null=True)  # Field name made lowercase.
    editor3firstname = models.TextField(db_column='Editor3Firstname', blank=True, null=True)  # Field name made lowercase.
    editor4firstname = models.TextField(db_column='Editor4Firstname', blank=True, null=True)  # Field name made lowercase.
    editor4surname = models.TextField(db_column='Editor4Surname', blank=True, null=True)  # Field name made lowercase.
    author4firstname = models.TextField(db_column='Author4Firstname', blank=True, null=True)  # Field name made lowercase.
    author4surname = models.TextField(db_column='Author4Surname', blank=True, null=True)  # Field name made lowercase.
    translator1firstname = models.TextField(db_column='Translator1Firstname', blank=True, null=True)  # Field name made lowercase.
    translator1surname = models.TextField(db_column='Translator1Surname', blank=True, null=True)  # Field name made lowercase.
    url = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    creationdate = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Bibliography'
        app_label = "diamm_migrate"
