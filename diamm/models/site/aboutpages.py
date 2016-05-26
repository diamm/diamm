from django.db import models


class AboutPages(models.Model):
    class Meta:
        app_label = "diamm_site"

    title = models.CharField(max_length=200, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
