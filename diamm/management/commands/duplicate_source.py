import logging

import blessings
from django.core.management import BaseCommand
from django.db.models.signals import post_delete, post_save

from diamm.helpers.solr_helpers import solr_index, solr_index_many
from diamm.models import Image, Item, Page, Source
from diamm.serializers.search.item import ItemSearchSerializer
from diamm.serializers.search.source import SourceSearchSerializer
from diamm.signals.item_signals import delete_item, index_item
from diamm.signals.page_signals import (
    delete_image,
    delete_page,
    index_image,
    index_page,
)
from diamm.signals.source_signals import index_source

term = blessings.Terminal()
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("sourcekey", type=int)
        # parser.add_argument('-d',
        #                     "--dry",
        #                     dest="dry_run",
        #                     action="store_true",
        #                     default=False,
        #                     help="Dry run; don't actually save anything.")

    def handle(self, *args, **options):
        sourcekey = options["sourcekey"]

        # disable solr signals for this operation
        post_save.disconnect(index_item, sender=Item)
        post_save.disconnect(index_page, sender=Page)
        post_save.disconnect(index_image, sender=Image)
        post_save.disconnect(index_source, sender=Source)
        post_delete.disconnect(delete_item, sender=Item)
        post_delete.disconnect(delete_page, sender=Page)
        post_delete.disconnect(delete_image, sender=Image)

        # Fetch the old source directly
        old_source = Source.objects.get(pk=sourcekey)
        new_source = Source.objects.get(pk=sourcekey)

        log.info(term.yellow(f"Duplicating source {new_source.pk}"))
        new_source.pk = None
        new_source._state.adding = True
        new_source.shelfmark = f"{new_source.shelfmark} (Duplicate)"
        new_source.save()

        for pg in old_source.pages.all():
            log.info(term.blue(f"\tCopying page {pg.pk}"))
            pg.legacy_id = f"{old_source.pk}_{pg.pk}"
            old_page = Page.objects.get(pk=pg.pk)
            pg.pk = None
            pg.source = new_source
            pg.save()

            for img in old_page.images.all():
                log.info(term.green(f"\t\tCopying image {img.pk}"))
                img.pk = None
                img.page = pg
                img.save()

        for itm in old_source.inventory.all():
            log.info(term.blue(f"\tCopying item {itm.pk}"))
            old_item = Item.objects.get(pk=itm.pk)
            itm.pk = None
            itm.source = new_source
            itm.save()
            itm.pages.clear()

            old_pages = old_item.pages.all()
            for pg in old_pages:
                log.info(term.green(f"\t\tAdding new page in item {pg.pk}"))
                new_pg = Page.objects.get(legacy_id=f"{old_source.pk}_{pg.pk}")
                itm.pages.add(new_pg)

            itm.save()

        new_source.save()

        solr_index(SourceSearchSerializer, new_source)
        solr_index_many(ItemSearchSerializer, new_source.inventory.all())

        print(term.yellow(f"Success, created new Source {new_source.pk}"))
