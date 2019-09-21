import pysolr
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Emptying Solr")
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        connection.delete(q="*:*")
