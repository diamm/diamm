from django.db import models


class LegacySource(models.Model):
    archive = models.TextField(blank=True, null=True)
    bibliography_orig_abbrevs = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    ccmabbrev = models.TextField(db_column='CCMabbrev', blank=True, null=True)  # Field name made lowercase.
    city = models.TextField(blank=True, null=True)
    completems = models.TextField(db_column='completeMS', blank=True, null=True)  # Field name made lowercase.
    dateofsource = models.TextField(db_column='dateOfSource', blank=True, null=True)  # Field name made lowercase.
    description_rism = models.TextField(db_column='description_RISM', blank=True, null=True)  # Field name made lowercase.
    done = models.TextField(blank=True, null=True)
    eecm = models.TextField(db_column='EECM', blank=True, null=True)  # Field name made lowercase.
    enddate = models.TextField(blank=True, null=True)
    folio = models.TextField(blank=True, null=True)
    format = models.TextField(blank=True, null=True)
    archivekey = models.DecimalField(db_column='archiveKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    lost = models.TextField(db_column='Lost', blank=True, null=True)  # Field name made lowercase.
    mixedsource = models.TextField(blank=True, null=True)
    notation = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    olim_text_only = models.TextField(blank=True, null=True)
    pagemeasurements = models.TextField(db_column='pageMeasurements', blank=True, null=True)  # Field name made lowercase.
    phase = models.TextField(db_column='Phase', blank=True, null=True)  # Field name made lowercase.
    rismccm = models.TextField(db_column='RISMCCM', blank=True, null=True)  # Field name made lowercase.
    rismabbrev = models.TextField(db_column='RISMabbrev', blank=True, null=True)  # Field name made lowercase.
    rismimagefilename1 = models.TextField(db_column='RISMimagefilename1', blank=True, null=True)  # Field name made lowercase.
    rismimagefilename2 = models.TextField(db_column='RISMimagefilename2', blank=True, null=True)  # Field name made lowercase.
    rismimagefilename3 = models.TextField(db_column='RISMimagefilename3', blank=True, null=True)  # Field name made lowercase.
    rismtext = models.TextField(db_column='RISMtext', blank=True, null=True)  # Field name made lowercase.
    shelfmark = models.TextField(db_column='shelfMark', blank=True, null=True)  # Field name made lowercase.
    sourcekey = models.IntegerField(db_column='sourceKey', primary_key=True)  # Field name made lowercase.
    startdate = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    surface = models.TextField(blank=True, null=True)
    webpermission = models.TextField(blank=True, null=True)
    uvshots = models.TextField(db_column='UVshots', blank=True, null=True)  # Field name made lowercase.
    measurementunits = models.TextField(blank=True, null=True)
    altrismabbrev = models.TextField(db_column='altRISMabbrev', blank=True, null=True)  # Field name made lowercase.
    setkey = models.DecimalField(db_column='setKey', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase.
    watermark = models.TextField(blank=True, null=True)
    sourcename = models.TextField(db_column='sourceName', blank=True, null=True)  # Field name made lowercase.
    sourcetype = models.TextField(db_column='sourceType', blank=True, null=True)  # Field name made lowercase.
    motetshelfmark = models.TextField(db_column='MOTETshelfmark', blank=True, null=True)  # Field name made lowercase.
    dedicatee = models.TextField(db_column='Dedicatee', blank=True, null=True)  # Field name made lowercase.
    dedicator = models.TextField(db_column='Dedicator', blank=True, null=True)  # Field name made lowercase.
    scribepublisher = models.TextField(db_column='scribePublisher', blank=True, null=True)  # Field name made lowercase.
    editor = models.TextField(blank=True, null=True)
    establishmentpatron = models.TextField(db_column='EstablishmentPatron', blank=True, null=True)  # Field name made lowercase.
    startdatemotet = models.TextField(db_column='startdateMotet', blank=True, null=True)  # Field name made lowercase.
    enddatemotet = models.TextField(db_column='enddateMotet', blank=True, null=True)  # Field name made lowercase.
    intdatemotet = models.TextField(db_column='intDateMotet', blank=True, null=True)  # Field name made lowercase.
    dedicationtext = models.TextField(db_column='dedicationText', blank=True, null=True)  # Field name made lowercase.
    datecomments = models.TextField(db_column='dateComments', blank=True, null=True)  # Field name made lowercase.
    liminarytext = models.TextField(db_column='liminaryText', blank=True, null=True)  # Field name made lowercase.
    provenancecity = models.TextField(db_column='ProvenanceCity', blank=True, null=True)  # Field name made lowercase.
    provenanceregion = models.TextField(db_column='ProvenanceRegion', blank=True, null=True)  # Field name made lowercase.
    provenancecitation = models.TextField(db_column='ProvenanceCitation', blank=True, null=True)  # Field name made lowercase.
    provenancecomment = models.TextField(db_column='provenanceComment', blank=True, null=True)  # Field name made lowercase.
    provenancecountry = models.TextField(db_column='ProvenanceCountry', blank=True, null=True)  # Field name made lowercase.
    ccmreset = models.TextField(db_column='CCMreset', blank=True, null=True)  # Field name made lowercase.
    rismreset = models.TextField(db_column='RISMreset', blank=True, null=True)  # Field name made lowercase.
    inventory = models.TextField(blank=True, null=True)
    modification_date = models.TextField(blank=True, null=True)
    stavegauge = models.TextField(db_column='staveGauge', blank=True, null=True)  # Field name made lowercase.
    bibliography_gathered = models.TextField(blank=True, null=True)
    ccmreset_2 = models.TextField(db_column='CCMreset_2', blank=True, null=True)  # Field name made lowercase.
    abbrevs_checked = models.TextField(blank=True, null=True)
    sortorder = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    description_diamm = models.TextField(db_column='description_DIAMM', blank=True, null=True)  # Field name made lowercase.
    duplicates_temp = models.TextField(db_column='Duplicates_temp', blank=True, null=True)  # Field name made lowercase.
    usedescription_for_tag = models.TextField(db_column='useDescription_for_tag', blank=True, null=True)  # Field name made lowercase.
    authority = models.TextField(blank=True, null=True)
    moved_y = models.TextField(db_column='moved_Y', blank=True, null=True)  # Field name made lowercase.
    numbering_source = models.TextField(blank=True, null=True)
    alt_numbering_source = models.TextField(blank=True, null=True)
    numberofleaves = models.TextField(db_column='numberofLeaves', blank=True, null=True)  # Field name made lowercase.
    earpdesignation = models.TextField(db_column='EarpDesignation', blank=True, null=True)  # Field name made lowercase.
    description_ccm = models.TextField(db_column='description_CCM', blank=True, null=True)  # Field name made lowercase.
    ccmimagefilename1 = models.TextField(db_column='CCMimagefilename1', blank=True, null=True)  # Field name made lowercase.
    ccmimagefilename2 = models.TextField(db_column='CCMimagefilename2', blank=True, null=True)  # Field name made lowercase.
    ccmimagefilename3 = models.TextField(db_column='CCMimagefilename3', blank=True, null=True)  # Field name made lowercase.
    description_author = models.TextField(blank=True, null=True)
    external_urls = models.TextField(db_column='external_URLs', blank=True, null=True)  # Field name made lowercase.
    externalurl = models.TextField(db_column='externalURL', blank=True, null=True)  # Field name made lowercase.
    externalurltitle = models.TextField(db_column='externalURLtitle', blank=True, null=True)  # Field name made lowercase.
    quotes = models.TextField(blank=True, null=True)
    copyrightstatement = models.TextField(blank=True, null=True)
    generaldescription = models.TextField(db_column='generalDescription', blank=True, null=True)  # Field name made lowercase.
    decoration = models.TextField(blank=True, null=True)
    binding = models.TextField(blank=True, null=True)
    leafnumberingsystem = models.TextField(db_column='leafNumberingSystem', blank=True, null=True)  # Field name made lowercase.
    leafnumberingdescription = models.TextField(db_column='leafNumberingDescription', blank=True, null=True)  # Field name made lowercase.
    othernumberings = models.TextField(db_column='otherNumberings', blank=True, null=True)  # Field name made lowercase.
    contentssummary = models.TextField(db_column='contentsSummary', blank=True, null=True)  # Field name made lowercase.
    condition = models.TextField(blank=True, null=True)
    description_ccm_james = models.TextField(db_column='description_CCM_James', blank=True, null=True)  # Field name made lowercase.
    description_rism_james = models.TextField(db_column='description_RISM_James', blank=True, null=True)  # Field name made lowercase.
    description_diamm_james = models.TextField(db_column='description_DIAMM_James', blank=True, null=True)  # Field name made lowercase.
    index = models.TextField(blank=True, null=True)
    description_prexml_output_for_james = models.TextField(db_column='description_preXML_output_for_James', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Source'
        app_label = "diamm_migrate"
