from django.core.management import BaseCommand

from diamm.models import Item


class Command(BaseCommand):
    def handle(self, *args, **options):
        items_changed = 0
        items = Item.objects.filter(
            composition__in=[
                25195,
                25800,
                30663,
                30717,
                31304,
                36353,
                37019,
                69756,
                86886,
                86928,
                87154,
                88223,
                88509,
                89627,
                90257,
                92829,
                92830,
                92831,
                92832,
                92832,
                93277,
                93399,
                97429,
                97950,
                100468,
                101909,
                101909,
                105556,
                105557,
                107969,
                110164,
                110198,
                110249,
                111838,
                111839,
            ]
        ).select_related("composition")
        for item in items:
            if not item.composition:
                continue

            composition_title = item.composition.title
            item.item_title = composition_title
            item.composition = None
            item.save()
            items_changed += 1

        self.stdout.write(f"{items_changed} items changed")
