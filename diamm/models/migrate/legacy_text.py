from django.db import models


class LegacyText(models.Model):
    class Meta:
        managed = False
        db_table = 'Text'
        app_label = "diamm_migrate"

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
