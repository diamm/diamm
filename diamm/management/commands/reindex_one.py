import pysolr
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("source_id", type=int)

    def handle(self, *args, **options):
        print("Emptying Solr")
        connection = pysolr.Solr(settings.SOLR["SERVER"])
        connection.delete(q="*:*")

    def index_source(self, pk):
        pass

    def index_pages(self, pk):
        pass

    def index_inventory(self, pk):
        pass
