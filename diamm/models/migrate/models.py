# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desidered behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models



class AuthorbibliographyIs(models.Model):
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alauthorkey = models.DecimalField(db_column='alAuthorKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    author_editor = models.TextField(blank=True, null=True)
    authorbibliography = models.IntegerField(db_column='authorBibliography', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AuthorBibliography_IS'


class BiblcomposerIs(models.Model):
    composerkey = models.DecimalField(db_column='composerKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    biblabbrev = models.TextField(db_column='biblAbbrev', blank=True, null=True)  # Field name made lowercase.
    bibliographycomposerkey = models.IntegerField(db_column='bibliographyComposerKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BiblComposer_IS'


class BiblcompositionIs(models.Model):
    compositionkey = models.DecimalField(db_column='compositionKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    biblabbrev = models.TextField(db_column='biblAbbrev', blank=True, null=True)  # Field name made lowercase.
    bibliographycompositionkey = models.IntegerField(db_column='bibliographyCompositionKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BiblComposition_IS'


class Bibliography(models.Model):
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





class Composition(models.Model):
    compositionkey = models.IntegerField(db_column='compositionKey', primary_key=True)  # Field name made lowercase.
    genre = models.TextField(blank=True, null=True)
    max_number_of_voices = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    composition_name = models.TextField(blank=True, null=True)
    isorhythmic = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Composition'


class Item(models.Model):
    itemkey = models.IntegerField(db_column='itemKey', primary_key=True)  # Field name made lowercase.
    incipitfilename = models.TextField(db_column='incipitFilename', blank=True, null=True)  # Field name made lowercase.
    positionms = models.DecimalField(db_column='positionMS', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    folios = models.TextField(db_column='Folios', blank=True, null=True)  # Field name made lowercase.
    positionpage = models.TextField(db_column='positionPage', blank=True, null=True)  # Field name made lowercase.
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    piecenumber = models.TextField(blank=True, null=True)
    datecomposed = models.TextField(db_column='dateComposed', blank=True, null=True)  # Field name made lowercase.
    datecopied = models.TextField(db_column='dateCopied', blank=True, null=True)  # Field name made lowercase.
    genre = models.TextField(blank=True, null=True)
    concordances = models.TextField(blank=True, null=True)
    musicnotationstylekey = models.DecimalField(db_column='musicNotationStyleKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    musiccolour = models.TextField(blank=True, null=True)
    restligatureconfig = models.TextField(blank=True, null=True)
    commentsonhands = models.TextField(blank=True, null=True)
    incipittranscription = models.TextField(db_column='incipitTranscription', blank=True, null=True)  # Field name made lowercase.
    novoices = models.TextField(db_column='noVoices', blank=True, null=True)  # Field name made lowercase.
    corrections = models.TextField(blank=True, null=True)
    layout = models.TextField(blank=True, null=True)
    abbrevposn = models.TextField(db_column='abbrevPosn', blank=True, null=True)  # Field name made lowercase.
    genrekey = models.DecimalField(db_column='genreKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    altincipitfilename = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    copyingstyle = models.TextField(blank=True, null=True)
    altincipititemkey = models.DecimalField(db_column='altincipititemKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    composeroriginal = models.TextField(db_column='composerOriginal', blank=True, null=True)  # Field name made lowercase.
    edition = models.TextField(blank=True, null=True)
    pars = models.TextField(blank=True, null=True)
    musicalgenre = models.TextField(db_column='musicalGenre', blank=True, null=True)  # Field name made lowercase.
    orderno = models.DecimalField(db_column='orderNo', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    folio_start = models.TextField(blank=True, null=True)
    folio_end = models.TextField(blank=True, null=True)
    compositionkey = models.DecimalField(db_column='compositionKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    catalogdesignation = models.TextField(db_column='catalogDesignation', blank=True, null=True)  # Field name made lowercase.
    foliationpagination = models.TextField(db_column='foliationPagination', blank=True, null=True)  # Field name made lowercase.
    musicalincipitscore = models.TextField(db_column='musicalIncipitScore', blank=True, null=True)  # Field name made lowercase.
    composerstandard = models.TextField(db_column='composerStandard', blank=True, null=True)  # Field name made lowercase.
    folio_start_alt = models.TextField(blank=True, null=True)
    folio_end_alt = models.TextField(blank=True, null=True)
    alt_numbering = models.TextField(blank=True, null=True)
    parstitle = models.TextField(db_column='parsTitle', blank=True, null=True)  # Field name made lowercase.
    parsorderno = models.DecimalField(db_column='parsOrderNo', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    textnotationcolour = models.TextField(db_column='textNotationColour', blank=True, null=True)  # Field name made lowercase.
    textnotationstylekey = models.TextField(db_column='textNotationStyleKey', blank=True, null=True)  # Field name made lowercase.
    texttype = models.TextField(db_column='textType', blank=True, null=True)  # Field name made lowercase.
    creationdate = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Item'


class Alaffiliation(models.Model):
    alaffiliationkey = models.IntegerField(db_column='alaffiliationKey', primary_key=True)  # Field name made lowercase.
    affiliation = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alAffiliation'




class Alclef(models.Model):
    alclefkey = models.IntegerField(db_column='alClefKey', primary_key=True)  # Field name made lowercase.
    clef = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alClef'



class Alcopyisttype(models.Model):
    copyisttype = models.TextField(db_column='copyistType', blank=True, null=True)  # Field name made lowercase.
    alcopyisttypekey = models.IntegerField(db_column='alcopyistTypeKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alCopyistType'


class Alcycletype(models.Model):
    alcycletypekey = models.IntegerField(db_column='alCycleTypeKey', primary_key=True)  # Field name made lowercase.
    cycletype = models.TextField(db_column='cycleType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alCycleType'


class Algenre(models.Model):
    algenrekey = models.IntegerField(db_column='alGenreKey', primary_key=True)  # Field name made lowercase.
    genre = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alGenre'


class Allanguage(models.Model):
    allangaugekey = models.IntegerField(db_column='alLangaugeKey', primary_key=True)  # Field name made lowercase.
    language = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alLanguage'


class Almensuration(models.Model):
    almensurationkey = models.IntegerField(db_column='alMensurationKey', primary_key=True)  # Field name made lowercase.
    mensurationsign = models.TextField(db_column='mensurationSign', blank=True, null=True)  # Field name made lowercase.
    mensurationtext = models.TextField(db_column='mensurationText', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alMensuration'


class Alnotationtype(models.Model):
    alnotationtypekey = models.IntegerField(primary_key=True)
    notation_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alNotationType'





class Alpersonrelationship(models.Model):
    alpersonrelationshipkey = models.IntegerField(db_column='alPersonRelationshipKey', primary_key=True)  # Field name made lowercase.
    relationshiptype = models.TextField(db_column='relationshipType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alPersonRelationship'


class Alprovenance(models.Model):
    alprovenancekey = models.IntegerField(db_column='alProvenanceKey', primary_key=True)  # Field name made lowercase.
    country = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alProvenance'


class Alsettype(models.Model):
    alsettypekey = models.IntegerField(db_column='alsetTypeKey', primary_key=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alSetType'


class Alvoice(models.Model):
    alvoicekey = models.IntegerField(db_column='alVoiceKey', primary_key=True)  # Field name made lowercase.
    voice = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alVoice'
