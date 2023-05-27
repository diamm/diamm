from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_index, solr_index_many, solr_delete, solr_delete_many
from diamm.models.data.source import Source
from diamm.serializers.search.item import ItemSearchSerializer
from diamm.serializers.search.source import SourceSearchSerializer
from diamm.serializers.search.composer_inventory import ComposerInventorySearchSerializer


@receiver(post_save, sender=Source)
def index_source(sender, instance, created, **kwargs):
    solr_index(SourceSearchSerializer, instance)
    solr_index_many(ItemSearchSerializer, instance.inventory.all())
    solr_index_many(ComposerInventorySearchSerializer)


@receiver(post_delete, sender=Source)
def delete_source(sender, instance, **kwargs):
    solr_delete(instance)
    solr_delete_many(instance.inventory.all())

