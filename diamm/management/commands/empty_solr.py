from django.conf import settings
from django.core.management.base import BaseCommand

from diamm.helpers.solr import SolrClient


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Emptying Solr")
        client = SolrClient()
        client.delete_all(core=settings.SOLR["LIVE_CORE"])
        client.commit(core=settings.SOLR["LIVE_CORE"])
