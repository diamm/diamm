import threading

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_index, solr_index_many, solr_delete, solr_delete_many
from diamm.models.data.source import Source
from diamm.serializers.search.item import ItemSearchSerializer
from diamm.serializers.search.source import SourceSearchSerializer


@receiver(post_save, sender=Source)
def index_source(sender, instance, created, **kwargs):
    t = threading.Thread(target=_do_source_indexing, args=[instance])
    t.daemon = True
    t.start()
    # solr_index(SourceSearchSerializer, instance)
    # solr_index_many(ItemSearchSerializer, instance.inventory.all())


@receiver(post_delete, sender=Source)
def delete_source(sender, instance, **kwargs):
    t = threading.Thread(target=_do_source_delete, args=[instance])
    t.daemon = True
    t.start()
    # solr_delete(instance)
    # solr_delete_many(instance.inventory.all())


def _do_source_indexing(instance):
    solr_index(SourceSearchSerializer, instance)
    solr_index_many(ItemSearchSerializer, instance.inventory.select_related("composition").prefetch_related("composition__composers").all())


def _do_source_delete(instance):
    solr_delete(instance)
    solr_delete_many(instance.inventory.select_related().all())
