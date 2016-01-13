from django.db import models

class LegacyItemImage(models.Model):
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
        app_label = "diamm_migrate"
