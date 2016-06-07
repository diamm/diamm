from django.db import models


class AboutPages(models.Model):
    class Meta:
        app_label = "diamm_site"

    title = models.CharField(max_length=200, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    about_section = models.ForeignKey('diamm_site.AboutPages',
                                      related_name="aboutpages", blank=True, null=True)

    def __str__(self):
        return self.title
