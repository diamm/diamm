from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from diamm.models.data.source import Source


class SourceSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return Source.objects.all().only("pk", "updated").order_by("pk")

    def location(self, obj):
        return reverse("source-detail", kwargs={"pk": obj.pk})

    def lastmod(self, obj):
        return obj.updated
