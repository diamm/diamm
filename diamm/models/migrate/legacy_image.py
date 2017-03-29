from django.db import models


class LegacyImage(models.Model):
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
    type = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Image'
        app_label = "diamm_migrate"
