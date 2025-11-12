from django.db import models


class ProjectSources(models.Model):
    class Meta:
        app_label = "diamm_site"
        verbose_name_plural = "Project sources"

    project = models.CharField(max_length=128)
    slug = models.SlugField(
        help_text="A value for this project that is used in a filter. Auto-filled from the title, but it can be modified here. No spaces allowed, only lower-case letters and hyphens."
    )
    sources = models.ManyToManyField(
        "diamm_data.Source", related_name="projects", blank=True
    )

    def __str__(self):
        return self.project
