from django.db import models


class LegacySource(models.Model):
    ccmabbrev = models.TextField(db_column='CCMabbrev', blank=True, null=True)  # Field name made lowercase.
    completems = models.TextField(db_column='completeMS', blank=True, null=True)  # Field name made lowercase.
    dateofsource = models.TextField(db_column='dateOfSource', blank=True, null=True)  # Field name made lowercase.
    description_rism = models.TextField(db_column='description_RISM', blank=True, null=True)  # Field name made lowercase.
    done = models.TextField(blank=True, null=True)
    folio = models.TextField(blank=True, null=True)
    format = models.TextField(blank=True, null=True)
    archivekey = models.ForeignKey("diamm_migrate.LegacyArchive", db_column='archiveKey', blank=True, null=True)  # Field name made lowercase.
    notation = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    olim_text_only = models.TextField(blank=True, null=True)
    pagemeasurements = models.TextField(db_column='pageMeasurements', blank=True, null=True)  # Field name made lowercase.
    measurementunits = models.TextField(blank=True, null=True)
    rismccm = models.TextField(db_column='RISMCCM', blank=True, null=True)  # Field name made lowercase.
    rismabbrev = models.TextField(db_column='RISMabbrev', blank=True, null=True)  # Field name made lowercase.
    rismtext = models.TextField(db_column='RISMtext', blank=True, null=True)  # Field name made lowercase.
    shelfmark = models.TextField(db_column='shelfMark', blank=True, null=True)  # Field name made lowercase.
    sourcekey = models.IntegerField(db_column='sourceKey', primary_key=True)  # Field name made lowercase.
    startdate = models.TextField(blank=True, null=True)
    enddate = models.TextField(blank=True, null=True)
    surface = models.TextField(blank=True, null=True)
    webpermission = models.TextField(blank=True, null=True)
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
    rismimagefilename1 = models.TextField(db_column='RISMimagefilename1', blank=True, null=True)  # Field name made lowercase.
    rismimagefilename2 = models.TextField(db_column='RISMimagefilename2', blank=True, null=True)  # Field name made lowercase.
    rismimagefilename3 = models.TextField(db_column='RISMimagefilename3', blank=True, null=True)  # Field name made lowercase.
    description_author = models.TextField(blank=True, null=True)
    external_urls = models.TextField(db_column='external_URLs', blank=True, null=True)  # Field name made lowercase.
    copyrightstatement = models.TextField(blank=True, null=True)
    leafnumberingdescription = models.TextField(db_column='leafNumberingDescription', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Source'
        app_label = "diamm_migrate"
