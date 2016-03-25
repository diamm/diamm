from django.db import models


class ItemComposer(models.Model):
    class Meta:
        app_label = "diamm_data"

    item = models.ForeignKey("diamm_data.Item",
                             related_name="unattributed_composers")
    composer = models.ForeignKey("diamm_data.Person",
                                 related_name="unattributed_works")
    uncertain = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
