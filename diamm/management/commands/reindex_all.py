import logging
import timeit

from django.conf import settings
from django.core.management.base import BaseCommand

from diamm.serializers.search.archive import index_archives
from diamm.serializers.search.bibliography import index_bibliography
from diamm.serializers.search.composer_inventory import index_composer_inventory
from diamm.serializers.search.composition import index_compositions
from diamm.serializers.search.helpers import empty_solr_core, commit_changes, swap_cores
from diamm.serializers.search.item import index_items
from diamm.serializers.search.organization import index_organizations
from diamm.serializers.search.page import index_pages_and_images
from diamm.serializers.search.person import index_people
from diamm.serializers.search.set import index_sets
from diamm.serializers.search.source import index_sources

log = logging.getLogger("diamm")


class Command(BaseCommand):
    def handle(self, *args, **options):
        cfg = {
            "resultsize": 2000,
            "dry": False,
            "solr": {
                "server": settings.SOLR["BASE_SERVER"],
                "indexing_core": settings.SOLR["INDEX_CORE"],
                "live_core": settings.SOLR["LIVE_CORE"],
            },
        }
        start = timeit.default_timer()
        success: bool = empty_solr_core(cfg)
        success &= index_sources(cfg)
        success &= index_items(cfg)
        success &= index_composer_inventory(cfg)
        success &= index_compositions(cfg)
        success &= index_archives(cfg)
        success &= index_people(cfg)
        success &= index_organizations(cfg)
        success &= index_pages_and_images(cfg)
        success &= index_bibliography(cfg)
        success &= index_sets(cfg)
        success &= commit_changes(cfg)
        success &= swap_cores(cfg)
        end = timeit.default_timer()
        elapsed: float = end - start

        hours, remainder = divmod(elapsed, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        log.info("Total time to index: %02i:%02i:%02.2f", hours, minutes, seconds)

        log.info(f"Success: {success}")
