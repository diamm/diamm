from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from diamm.models.data.item import Item
from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.serializers.search.source import SourceSearchSerializer
from diamm.serializers.search.composition import CompositionSearchSerializer
from diamm.serializers.search.item import ItemSearchSerializer


@receiver(post_save, sender=Item)
def index_item(sender, instance, created, **kwargs):
    solr_index(ItemSearchSerializer, instance)
    solr_index(SourceSearchSerializer, instance.source)
    solr_index(CompositionSearchSerializer, instance.composition)


@receiver(post_delete, sender=Item)
def delete_item(sender, instance, **kwargs):
    solr_delete(instance)
    solr_index(SourceSearchSerializer, instance.source)
    solr_index(CompositionSearchSerializer, instance.composition)
