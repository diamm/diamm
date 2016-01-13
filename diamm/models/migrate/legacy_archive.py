from django.db import models


class LegacyArchive(models.Model):
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
    alcountrykey = models.IntegerField(db_column='alCountryKey', blank=True, null=True)  # Field name made lowercase.
    alcitykey = models.IntegerField(db_column='alCityKey', blank=True, null=True)  # Field name made lowercase.
    sourcesfromthisarchive = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    banner_url = models.TextField(db_column='banner_URL', blank=True, null=True)  # Field name made lowercase.
    library_type = models.TextField(blank=True, null=True)
    specialcase = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Archive'
        app_label = "diamm_migrate"
