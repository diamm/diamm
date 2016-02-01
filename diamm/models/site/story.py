from django.db import models


class Story(models.Model):
    class Meta:
        app_label = "diamm_site"
        verbose_name_plural = "stories"

    title = models.CharField(max_length=256)
    body = models.TextField()
    tags = models.ManyToManyField("diamm_site.Tag", blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
