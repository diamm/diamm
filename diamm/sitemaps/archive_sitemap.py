from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from diamm.models.data.archive import Archive


class ArchiveSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return Archive.objects.all().only("pk", "updated").order_by("pk")

    def location(self, obj):
        return reverse("archive-detail", kwargs={"pk": obj.pk})

    def lastmod(self, obj):
        return obj.updated
