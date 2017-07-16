from django.db import models


class ItemComposer(models.Model):
    class Meta:
        app_label = "diamm_data"

    COMPOSER_HELP_TEXT = """DO NOT attach a duplicate composer here if this item is attached to a composition.
                            This field is ONLY to be used to record that a MSS features works by a particular composer,
                            and should not be used otherwise."""

    item = models.ForeignKey("diamm_data.Item",
                             related_name="unattributed_composers")
    composer = models.ForeignKey("diamm_data.Person",
                                 related_name="unattributed_works",
                                 help_text=COMPOSER_HELP_TEXT)
    uncertain = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
