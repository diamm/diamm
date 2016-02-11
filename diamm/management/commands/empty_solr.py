from django.core.management.base import BaseCommand
from django.conf import settings
import pysolr


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Emptying Solr")
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        connection.delete(q="*:*")
