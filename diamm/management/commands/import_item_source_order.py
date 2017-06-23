import csv
from django.db.models import signals
from django.core.management import BaseCommand
from diamm.models.data.item import Item
from diamm.signals.item_signals import index_item, delete_item


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv', type=str)

    def handle(self, *args, **options):
        signals.post_save.disconnect(index_item, sender=Item)

        with open(options['csv'], 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    it = Item.objects.get(pk=row['itemKey'])
                    it.source_order = int(float(row['orderNo']))
                    it.save()
                except Item.DoesNotExist:
                    print("Item {0} does not exist".format(row['itemKey']))