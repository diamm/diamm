from django.db import models


class LegacyCompositionComposer(models.Model):
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
        app_label = "diamm_migrate"
