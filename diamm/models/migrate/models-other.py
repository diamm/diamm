# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Archive(models.Model):
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    address3 = models.TextField(blank=True, null=True)
    address4 = models.TextField(blank=True, null=True)
    address5 = models.TextField(blank=True, null=True)
    address6 = models.TextField(blank=True, null=True)
    address7 = models.TextField(blank=True, null=True)
    address8 = models.TextField(blank=True, null=True)
    archivenameoriginal = models.TextField(db_column='archiveNameOriginal', blank=True, null=True)  # Field name made lowercase.
    availableonwebsite = models.TextField(db_column='availableOnWebsite', blank=True, null=True)  # Field name made lowercase.
    cdcopiessent = models.TextField(db_column='CDcopiessent', blank=True, null=True)  # Field name made lowercase.
    city = models.TextField(blank=True, null=True)
    copyrightholder = models.TextField(blank=True, null=True)
    correspondencestatus = models.TextField(blank=True, null=True)
    currentstatus = models.TextField(blank=True, null=True)
    done = models.TextField(db_column='DONE', blank=True, null=True)  # Field name made lowercase.
    email = models.TextField(blank=True, null=True)
    emailed = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    ftp = models.TextField(blank=True, null=True)
    furthercorrespondence = models.TextField(blank=True, null=True)
    archivekey = models.IntegerField(db_column='archiveKey', primary_key=True)  # Field name made lowercase.
    imagesarchived = models.TextField(blank=True, null=True)
    imagesordered = models.TextField(blank=True, null=True)
    imagesreceived = models.TextField(blank=True, null=True)
    invoicepaid = models.TextField(blank=True, null=True)
    invoicequeried = models.TextField(blank=True, null=True)
    letterfromj = models.TextField(db_column='letterfromJ', blank=True, null=True)  # Field name made lowercase.
    librariana = models.TextField(db_column='librarianA', blank=True, null=True)  # Field name made lowercase.
    librarianb = models.TextField(db_column='librarianB', blank=True, null=True)  # Field name made lowercase.
    licencenumbers = models.TextField(blank=True, null=True)
    licencestatus = models.TextField(blank=True, null=True)
    licencescompleted = models.TextField(blank=True, null=True)
    listofsources = models.TextField(blank=True, null=True)
    daysrequired = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    imagesfromthisarchive = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    ok = models.TextField(db_column='OK', blank=True, null=True)  # Field name made lowercase.
    omit = models.TextField(blank=True, null=True)
    personalcontact = models.TextField(blank=True, null=True)
    phase = models.TextField(db_column='Phase', blank=True, null=True)  # Field name made lowercase.
    postprocessingdone = models.TextField(blank=True, null=True)
    preliminary = models.TextField(blank=True, null=True)
    readyforvisit = models.TextField(blank=True, null=True)
    replyreceived = models.TextField(blank=True, null=True)
    requirespatc = models.TextField(db_column='requiresPATC', blank=True, null=True)  # Field name made lowercase.
    responsefrom = models.TextField(blank=True, null=True)
    responsefromdate = models.TextField(blank=True, null=True)
    salutation = models.TextField(blank=True, null=True)
    siglum = models.TextField(blank=True, null=True)
    someoutstanding = models.TextField(blank=True, null=True)
    telephone = models.TextField(blank=True, null=True)
    telephoned = models.DateField(blank=True, null=True)
    totaldays = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    totalimages = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    totalcity = models.TextField(blank=True, null=True)
    updated = models.DateField(blank=True, null=True)
    url_original = models.TextField(blank=True, null=True)
    visitdates = models.TextField(blank=True, null=True)
    worthprodding = models.TextField(blank=True, null=True)
    written = models.DateField(blank=True, null=True)
    cdschecked = models.TextField(db_column='CDschecked', blank=True, null=True)  # Field name made lowercase.
    fulladdressrunon = models.TextField(blank=True, null=True)
    invoicereceived = models.TextField(blank=True, null=True)
    alcountrykey = models.DecimalField(db_column='alCountryKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alcitykey = models.DecimalField(db_column='alCityKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    sourcesfromthisarchive = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    banner_url = models.TextField(db_column='banner_URL', blank=True, null=True)  # Field name made lowercase.
    library_type = models.TextField(blank=True, null=True)
    specialcase = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Archive'


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


class BiblitemIs(models.Model):
    itemkey = models.DecimalField(db_column='itemKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    biblabbrev = models.TextField(db_column='biblAbbrev', blank=True, null=True)  # Field name made lowercase.
    bibliographyitemkey = models.IntegerField(db_column='bibliographyItemKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BiblItem_IS'


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
    novolumes = models.TextField(db_column='noVolumes', blank=True, null=True)  # Field name made lowercase.
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


class BibliographysourceIs(models.Model):
    bibliographykey = models.DecimalField(db_column='bibliographyKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    page = models.TextField(blank=True, null=True)
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    biblabbrev = models.TextField(db_column='BiblAbbrev', blank=True, null=True)  # Field name made lowercase.
    bibliographysourcekey = models.IntegerField(db_column='bibliographySourceKey', primary_key=True)  # Field name made lowercase.
    composerkey = models.DecimalField(db_column='composerKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    primarystudy = models.TextField(db_column='primaryStudy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BibliographySource_IS'


class Composer(models.Model):
    lastnameoriginal = models.TextField(db_column='lastNameOriginal', blank=True, null=True)  # Field name made lowercase.
    composerkey = models.IntegerField(db_column='composerKey', primary_key=True)  # Field name made lowercase.
    sourcekey = models.TextField(db_column='sourceKey', blank=True, null=True)  # Field name made lowercase.
    firstname = models.TextField(db_column='firstName', blank=True, null=True)  # Field name made lowercase.
    dates_public = models.TextField(blank=True, null=True)
    variantspellings = models.TextField(blank=True, null=True)
    itemkey = models.TextField(db_column='itemKey', blank=True, null=True)  # Field name made lowercase.
    tngentry = models.TextField(db_column='TNGentry', blank=True, null=True)  # Field name made lowercase.
    date_earliest = models.TextField(blank=True, null=True)
    date_latest = models.TextField(blank=True, null=True)
    date_floruit_earliest = models.TextField(blank=True, null=True)
    info_source = models.TextField(blank=True, null=True)
    date_floruit_latest = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Composer'


class Composition(models.Model):
    attribution_authority = models.TextField(blank=True, null=True)
    attribution_uncertain = models.TextField(blank=True, null=True)
    compositionkey = models.IntegerField(db_column='compositionKey', primary_key=True)  # Field name made lowercase.
    genre = models.TextField(blank=True, null=True)
    max_number_of_voices = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    composition_name = models.TextField(blank=True, null=True)
    composerattribution = models.TextField(db_column='composerAttribution', blank=True, null=True)  # Field name made lowercase.
    isorhythmic = models.TextField(blank=True, null=True)
    title = models.TextField(db_column='TITLE', blank=True, null=True)  # Field name made lowercase.
    notesconcordances = models.TextField(blank=True, null=True)
    concordancescollated = models.TextField(db_column='concordancesCollated', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Composition'


class CompositioncomposerIs(models.Model):
    composerkey = models.DecimalField(db_column='composerKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    firstname = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    compositioncomposerkey = models.IntegerField(db_column='compositionComposerKey', primary_key=True)  # Field name made lowercase.
    composernamebasic = models.TextField(db_column='composerNamebasic', blank=True, null=True)  # Field name made lowercase.
    compositionkey = models.DecimalField(db_column='compositionKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    attribution_uncertain = models.TextField(blank=True, null=True)
    notes_attribution = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CompositionComposer_IS'


class Compositioncycle(models.Model):
    compositioncyclekey = models.IntegerField(db_column='compositionCycleKey', primary_key=True)  # Field name made lowercase.
    title = models.TextField(blank=True, null=True)
    title_model_compositionkey = models.DecimalField(db_column='title_model_compositionKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    composerkey = models.DecimalField(db_column='composerKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    composer = models.TextField(blank=True, null=True)
    alcycletypekey = models.DecimalField(db_column='alCycleTypeKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CompositionCycle'


class Compositioncyclecomposition(models.Model):
    compositioncyclekey = models.DecimalField(db_column='compositionCycleKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    compositionkey = models.DecimalField(db_column='compositionKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    orderno = models.DecimalField(db_column='orderNo', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    positiontitle = models.TextField(db_column='positionTitle', blank=True, null=True)  # Field name made lowercase.
    compositioncyclecompositionkey = models.IntegerField(db_column='compositionCycleCompositionKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CompositionCycleComposition'


class Diammuser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=20, blank=True, null=True)
    displayname = models.CharField(db_column='displayName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    passwd = models.CharField(max_length=80, blank=True, null=True)
    email = models.CharField(max_length=80, blank=True, null=True)
    affiliation = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DiammUser'


class Image(models.Model):
    archive = models.TextField(blank=True, null=True)
    archivedfilename = models.TextField(blank=True, null=True)
    availwebsite = models.TextField(blank=True, null=True)
    bibliography = models.TextField(blank=True, null=True)
    brightness = models.TextField(blank=True, null=True)
    captureconditions = models.TextField(blank=True, null=True)
    capturedevice = models.TextField(blank=True, null=True)
    cd_dvdcopies = models.TextField(db_column='CD/DVDcopies', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    city = models.TextField(blank=True, null=True)
    contrast = models.TextField(blank=True, null=True)
    copyrightstatement = models.TextField(blank=True, null=True)
    cropping = models.TextField(blank=True, null=True)
    currentmeasurements = models.TextField(blank=True, null=True)
    datecreated = models.DateField(db_column='dateCreated', blank=True, null=True)  # Field name made lowercase.
    datecopied = models.TextField(db_column='dateCopied', blank=True, null=True)  # Field name made lowercase.
    detailfilename = models.TextField(blank=True, null=True)
    digitised = models.TextField(blank=True, null=True)
    eecmno = models.TextField(db_column='EECMno', blank=True, null=True)  # Field name made lowercase.
    vrauthor = models.TextField(db_column='VRauthor', blank=True, null=True)  # Field name made lowercase.
    vrdetails = models.TextField(db_column='VRdetails', blank=True, null=True)  # Field name made lowercase.
    existingimages = models.TextField(blank=True, null=True)
    fileformat = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    filters = models.TextField(blank=True, null=True)
    focus = models.TextField(blank=True, null=True)
    folio = models.TextField(blank=True, null=True)
    gamma = models.TextField(blank=True, null=True)
    id = models.DecimalField(db_column='ID', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    imagekey = models.IntegerField(db_column='imageKey', primary_key=True)  # Field name made lowercase.
    incipitimagefilename = models.TextField(blank=True, null=True)
    vrlayers = models.TextField(db_column='VRlayers', blank=True, null=True)  # Field name made lowercase.
    datemodified = models.DateField(db_column='dateModified', blank=True, null=True)  # Field name made lowercase.
    nocaptures = models.TextField(db_column='noCaptures', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    photographer = models.TextField(blank=True, null=True)
    questions = models.TextField(blank=True, null=True)
    rismimagefilename = models.TextField(db_column='RISMimagefilename', blank=True, null=True)  # Field name made lowercase.
    source = models.TextField(blank=True, null=True)
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    surfacematerial = models.TextField(db_column='surfaceMaterial', blank=True, null=True)  # Field name made lowercase.
    tsm = models.TextField(db_column='TSM', blank=True, null=True)  # Field name made lowercase.
    uv = models.TextField(db_column='UV', blank=True, null=True)  # Field name made lowercase.
    uvfilename = models.TextField(db_column='UVfilename', blank=True, null=True)  # Field name made lowercase.
    vrevaluation = models.TextField(db_column='VRevaluation', blank=True, null=True)  # Field name made lowercase.
    vrfilename = models.TextField(db_column='VRfilename', blank=True, null=True)  # Field name made lowercase.
    watermarkfilename = models.TextField(blank=True, null=True)
    rismimagefilename2 = models.TextField(db_column='RISMimagefilename2', blank=True, null=True)  # Field name made lowercase.
    archiveduvfilename = models.TextField(db_column='archivedUVfilename', blank=True, null=True)  # Field name made lowercase.
    archiveddetailfilename = models.TextField(blank=True, null=True)
    archivedwatermarkfilename = models.TextField(blank=True, null=True)
    archivedvrfilename = models.TextField(db_column='archivedVRfilename', blank=True, null=True)  # Field name made lowercase.
    watermark = models.TextField(blank=True, null=True)
    vr = models.TextField(db_column='VR', blank=True, null=True)  # Field name made lowercase.
    detail = models.TextField(blank=True, null=True)
    imagetype = models.TextField(blank=True, null=True)
    orderno = models.DecimalField(db_column='orderNo', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    checked = models.TextField(blank=True, null=True)
    folio_alt = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Image'


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


class ItemimageIs(models.Model):
    itemkey = models.DecimalField(db_column='itemKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    imagekey = models.DecimalField(db_column='imageKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    positiononpage = models.TextField(db_column='positiononPage', blank=True, null=True)  # Field name made lowercase.
    incipitfilename = models.TextField(blank=True, null=True)
    itemfolio = models.TextField(blank=True, null=True)
    itemimagekey = models.IntegerField(db_column='itemImageKey', primary_key=True)  # Field name made lowercase.
    initial = models.TextField(blank=True, null=True)
    initialcolour = models.TextField(db_column='initialColour', blank=True, null=True)  # Field name made lowercase.
    decorationcolour = models.TextField(db_column='decorationColour', blank=True, null=True)  # Field name made lowercase.
    decorationstyle = models.TextField(db_column='decorationStyle', blank=True, null=True)  # Field name made lowercase.
    imagefolio = models.TextField(blank=True, null=True)
    imageserial = models.DecimalField(db_column='imageSerial', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ItemImage_IS'


class NotationsourceIs(models.Model):
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alnotationtypekey = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    notationsourcekey = models.IntegerField(db_column='notationsourceKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'NotationSource_IS'


class Secondaryimage(models.Model):
    secondaryimagekey = models.IntegerField(db_column='secondaryImageKey', primary_key=True)  # Field name made lowercase.
    imagekey = models.DecimalField(db_column='ImageKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    filename = models.TextField(blank=True, null=True)
    imagetype = models.TextField(blank=True, null=True)
    archivefilename = models.TextField(blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    datemodified = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SecondaryImage'


class Set(models.Model):
    setkey = models.IntegerField(db_column='setKey', primary_key=True)  # Field name made lowercase.
    clustershelfmark = models.TextField(db_column='clusterShelfMark', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)
    bibliography = models.TextField(blank=True, null=True)
    settypekey = models.DecimalField(db_column='setTypeKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    g_key = models.DecimalField(db_column='g_Key', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Set'


class Source(models.Model):
    ccmabbrev = models.TextField(db_column='CCMabbrev', blank=True, null=True)  # Field name made lowercase.
    completems = models.TextField(db_column='completeMS', blank=True, null=True)  # Field name made lowercase.
    dateofsource = models.TextField(db_column='dateOfSource', blank=True, null=True)  # Field name made lowercase.
    description_rism = models.TextField(db_column='description_RISM', blank=True, null=True)  # Field name made lowercase.
    done = models.TextField(blank=True, null=True)
    enddate = models.TextField(blank=True, null=True)
    folio = models.TextField(blank=True, null=True)
    format = models.TextField(blank=True, null=True)
    archivekey = models.DecimalField(db_column='archiveKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    notation = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    olim_text_only = models.TextField(blank=True, null=True)
    pagemeasurements = models.TextField(db_column='pageMeasurements', blank=True, null=True)  # Field name made lowercase.
    rismccm = models.TextField(db_column='RISMCCM', blank=True, null=True)  # Field name made lowercase.
    rismabbrev = models.TextField(db_column='RISMabbrev', blank=True, null=True)  # Field name made lowercase.
    rismimagefilename1 = models.TextField(db_column='RISMimagefilename1', blank=True, null=True)  # Field name made lowercase.
    rismimagefilename2 = models.TextField(db_column='RISMimagefilename2', blank=True, null=True)  # Field name made lowercase.
    rismimagefilename3 = models.TextField(db_column='RISMimagefilename3', blank=True, null=True)  # Field name made lowercase.
    rismtext = models.TextField(db_column='RISMtext', blank=True, null=True)  # Field name made lowercase.
    shelfmark = models.TextField(db_column='shelfMark', blank=True, null=True)  # Field name made lowercase.
    sourcekey = models.IntegerField(db_column='sourceKey', primary_key=True)  # Field name made lowercase.
    startdate = models.TextField(blank=True, null=True)
    surface = models.TextField(blank=True, null=True)
    webpermission = models.TextField(blank=True, null=True)
    measurementunits = models.TextField(blank=True, null=True)
    altrismabbrev = models.TextField(db_column='altRISMabbrev', blank=True, null=True)  # Field name made lowercase.
    setkey = models.DecimalField(db_column='setKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    watermark = models.TextField(blank=True, null=True)
    sourcename = models.TextField(db_column='sourceName', blank=True, null=True)  # Field name made lowercase.
    sourcetype = models.TextField(db_column='sourceType', blank=True, null=True)  # Field name made lowercase.
    motetshelfmark = models.TextField(db_column='MOTETshelfmark', blank=True, null=True)  # Field name made lowercase.
    dedicatee = models.TextField(db_column='Dedicatee', blank=True, null=True)  # Field name made lowercase.
    dedicator = models.TextField(db_column='Dedicator', blank=True, null=True)  # Field name made lowercase.
    editor = models.TextField(blank=True, null=True)
    startdatemotet = models.TextField(db_column='startdateMotet', blank=True, null=True)  # Field name made lowercase.
    dedicationtext = models.TextField(db_column='dedicationText', blank=True, null=True)  # Field name made lowercase.
    datecomments = models.TextField(db_column='dateComments', blank=True, null=True)  # Field name made lowercase.
    liminarytext = models.TextField(db_column='liminaryText', blank=True, null=True)  # Field name made lowercase.
    provenancecity = models.TextField(db_column='ProvenanceCity', blank=True, null=True)  # Field name made lowercase.
    provenanceregion = models.TextField(db_column='ProvenanceRegion', blank=True, null=True)  # Field name made lowercase.
    provenancecitation = models.TextField(db_column='ProvenanceCitation', blank=True, null=True)  # Field name made lowercase.
    provenancecomment = models.TextField(db_column='provenanceComment', blank=True, null=True)  # Field name made lowercase.
    provenancecountry = models.TextField(db_column='ProvenanceCountry', blank=True, null=True)  # Field name made lowercase.
    modification_date = models.TextField(blank=True, null=True)
    stavegauge = models.TextField(db_column='staveGauge', blank=True, null=True)  # Field name made lowercase.
    description_diamm = models.TextField(db_column='description_DIAMM', blank=True, null=True)  # Field name made lowercase.
    authority = models.TextField(blank=True, null=True)
    alt_numbering_source = models.TextField(blank=True, null=True)
    earpdesignation = models.TextField(db_column='EarpDesignation', blank=True, null=True)  # Field name made lowercase.
    description_ccm = models.TextField(db_column='description_CCM', blank=True, null=True)  # Field name made lowercase.
    ccmimagefilename1 = models.TextField(db_column='CCMimagefilename1', blank=True, null=True)  # Field name made lowercase.
    ccmimagefilename2 = models.TextField(db_column='CCMimagefilename2', blank=True, null=True)  # Field name made lowercase.
    ccmimagefilename3 = models.TextField(db_column='CCMimagefilename3', blank=True, null=True)  # Field name made lowercase.
    description_author = models.TextField(blank=True, null=True)
    external_urls = models.TextField(db_column='external_URLs', blank=True, null=True)  # Field name made lowercase.
    copyrightstatement = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Source'


class SourceprovenanceIs(models.Model):
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alprovenancekey = models.DecimalField(db_column='alProvenanceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    uncertain = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    institution = models.TextField(blank=True, null=True)
    protectorate = models.TextField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    sourceprovenancekey = models.IntegerField(db_column='sourceProvenanceKey', primary_key=True)  # Field name made lowercase.
    institution_uncertain = models.TextField(blank=True, null=True)
    city_uncertain = models.TextField(blank=True, null=True)
    region_uncertain = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SourceProvenance_IS'


class SourcesetIs(models.Model):
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    setkey = models.DecimalField(db_column='setKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    sourcesetkey = models.IntegerField(db_column='sourceSetKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SourceSet_IS'


class SourceCopyistIs(models.Model):
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alcopyistkey = models.DecimalField(db_column='alcopyistKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alcopyisttypekey = models.DecimalField(db_column='alcopyistTypeKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    attribution_uncertain = models.TextField(blank=True, null=True)
    sourcecopyistkey = models.IntegerField(db_column='sourceCopyistKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Source_Copyist_IS'


class SourcePersonIs(models.Model):
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alpersonkey = models.DecimalField(db_column='alPersonKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alpersonrelationshipkey = models.DecimalField(db_column='alPersonRelationshipKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    attribution_uncertain = models.TextField(blank=True, null=True)
    sourcealpersonkey = models.IntegerField(db_column='sourceAlPersonKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Source_Person_IS'


class Text(models.Model):
    textkey = models.IntegerField(db_column='textKey', primary_key=True)  # Field name made lowercase.
    genre = models.TextField(db_column='Genre', blank=True, null=True)  # Field name made lowercase.
    itemkey = models.DecimalField(db_column='itemKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    voicepart = models.TextField(blank=True, null=True)
    clef = models.TextField(blank=True, null=True)
    folios = models.TextField(blank=True, null=True)
    sourcekey = models.DecimalField(db_column='sourceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    incipitfilename = models.TextField(blank=True, null=True)
    positiononpage = models.TextField(db_column='positiononPage', blank=True, null=True)  # Field name made lowercase.
    imagekey = models.TextField(db_column='imageKey', blank=True, null=True)  # Field name made lowercase.
    global_field = models.DecimalField(db_column='Global', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    orderno = models.DecimalField(db_column='orderNo', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    fulltermtext_authority = models.TextField(db_column='fulltermText_authority', blank=True, null=True)  # Field name made lowercase.
    alclefkey = models.DecimalField(db_column='alClefKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    alvoicekey = models.DecimalField(db_column='alVoiceKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    editorial_voicepart = models.TextField(blank=True, null=True)
    g_key = models.DecimalField(db_column='g_Key', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    canon = models.TextField(blank=True, null=True)
    almensurationkey = models.DecimalField(db_column='alMensurationKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    completelibraryinfo = models.TextField(db_column='completeLibraryInfo', blank=True, null=True)  # Field name made lowercase.
    fullitemtext_copy = models.TextField(db_column='fullItemText_Copy', blank=True, null=True)  # Field name made lowercase.
    standardspellingfulltext_copy = models.TextField(db_column='standardspellingFulltext_Copy', blank=True, null=True)  # Field name made lowercase.
    standardspellingincipit_copy = models.TextField(db_column='standardspellingIncipit_Copy', blank=True, null=True)  # Field name made lowercase.
    textincipit_copy = models.TextField(db_column='textincipit_Copy', blank=True, null=True)  # Field name made lowercase.
    languagegathered = models.TextField(db_column='languageGathered', blank=True, null=True)  # Field name made lowercase.
    mensuration = models.TextField(blank=True, null=True)
    signature = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Text'


class TextlanguageIs(models.Model):
    allanguagekey = models.DecimalField(db_column='alLanguageKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    textkey = models.DecimalField(db_column='textKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    textlanguagekey = models.IntegerField(db_column='textLanguageKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TextLanguage_IS'


class Alaffiliation(models.Model):
    alaffiliationkey = models.IntegerField(db_column='alaffiliationKey', primary_key=True)  # Field name made lowercase.
    affiliation = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alAffiliation'


class Alauthor(models.Model):
    alauthorkey = models.IntegerField(db_column='alAuthorKey', primary_key=True)  # Field name made lowercase.
    lastname = models.TextField(db_column='lastName', blank=True, null=True)  # Field name made lowercase.
    firstname = models.TextField(db_column='firstName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alAuthor'


class Alcity(models.Model):
    alcountrykey = models.DecimalField(db_column='alCountryKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    city = models.TextField(blank=True, null=True)
    alcitykey = models.IntegerField(db_column='alCityKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alCity'


class Alclef(models.Model):
    alclefkey = models.IntegerField(db_column='alClefKey', primary_key=True)  # Field name made lowercase.
    clef = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alClef'


class Alcopyist(models.Model):
    alcopyistkey = models.IntegerField(db_column='alcopyistKey', primary_key=True)  # Field name made lowercase.
    copyistname = models.TextField(db_column='copyistName', blank=True, null=True)  # Field name made lowercase.
    alaffiliationkey = models.DecimalField(db_column='alaffiliationKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alCopyist'


class Alcopyisttype(models.Model):
    copyisttype = models.TextField(db_column='copyistType', blank=True, null=True)  # Field name made lowercase.
    alcopyisttypekey = models.IntegerField(db_column='alcopyistTypeKey', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alCopyistType'


class Alcountry(models.Model):
    country = models.TextField(blank=True, null=True)
    alcountrykey = models.IntegerField(db_column='alcountryKey', primary_key=True)  # Field name made lowercase.
    abbreviation = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alCountry'


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


class Alperson(models.Model):
    alpersonkey = models.IntegerField(db_column='alPersonKey', primary_key=True)  # Field name made lowercase.
    alaffiliationkey = models.TextField(db_column='alaffiliationKey', blank=True, null=True)  # Field name made lowercase.
    surname = models.TextField(db_column='Surname', blank=True, null=True)  # Field name made lowercase.
    firstname = models.TextField(blank=True, null=True)
    startdate = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    startdate_approx = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    enddate_approx = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    enddate = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    aliases = models.TextField(blank=True, null=True)
    fullnameoriginal = models.TextField(db_column='fullNameOriginal', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alPerson'


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
