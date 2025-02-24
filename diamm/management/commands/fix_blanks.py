from django.core.management import BaseCommand

from diamm.models import Item


class Command(BaseCommand):
    def handle(self, *args, **options):
        items = Item.objects.filter(
            composition__in=[
                92829,
                111838,
                111839,
                87154,
                92832,
                86886,
                88223,
                97429,
            ]
        ).select_related("composition")
        for item in items:
            composition_title = item.composition.title
            item.item_title = composition_title
            item.composition = None
            item.save()
