from django.db import models


class LegacyItem(models.Model):
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
        app_label = "diamm_migrate"
