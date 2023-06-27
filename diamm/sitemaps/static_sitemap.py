from django.contrib.sitemaps import Sitemap
from wagtail.models import Site

DIAMM_SITE = 1


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return Site.objects.get(pk=DIAMM_SITE).root_page.get_descendants(inclusive=True).live().public().order_by('path')

    def location(self, page):
        return page.url
