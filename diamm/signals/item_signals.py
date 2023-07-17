from diamm.helpers.solr_helpers import solr_delete, solr_index, SolrConnection
from diamm.models.data.item import Item
from diamm.serializers.search.composer_inventory import ComposerInventorySearchSerializer, FIELDS_TO_INDEX
from diamm.serializers.search.composition import CompositionSearchSerializer
from diamm.serializers.search.item import ItemSearchSerializer
from diamm.serializers.search.source import SourceSearchSerializer
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver


def __composer_inventory_index(item):
    source = item.source

    if not source:
        return None

    # Delete this item in the indexed source from Solr.
    # conn = pysolr.Solr(settings.SOLR['SERVER'])
    fq = ["type:composerinventory",
          f"source_i:{source.pk}",
          f"item_i:{item.pk}"]
    records = SolrConnection.search("*:*", fq=fq, fl="id")
    if records.docs:
        for doc in records.docs:
            SolrConnection.delete(id=doc['id'])

    res = [list(o) for o in source.inventory.values_list(*FIELDS_TO_INDEX)]
    data = ComposerInventorySearchSerializer(res, many=True).data
    SolrConnection.add(data)
    SolrConnection.commit()


def __composer_inventory_delete(item):
    source = item.source
    # conn = pysolr.Solr(settings.SOLR['SERVER'])

    fq = ["type:composerinventory",
          f"source_i:{source.pk}",
          f"item_i:{item.pk}"]
    records = SolrConnection.search("*:*", fq=fq, fl="id")
    if records.docs:
        for doc in records.docs:
            SolrConnection.delete(id=doc['id'])

    SolrConnection.commit()

@receiver(post_save, sender=Item)
def index_item(sender, instance, created, **kwargs):
    solr_index(ItemSearchSerializer, instance)
    solr_index(SourceSearchSerializer, instance.source)
    if instance.composition:
        solr_index(CompositionSearchSerializer, instance.composition)

    __composer_inventory_index(instance)


@receiver(post_delete, sender=Item)
def delete_item(sender, instance, **kwargs):
    solr_delete(instance)
    solr_index(SourceSearchSerializer, instance.source)
    if instance.composition:
        solr_index(CompositionSearchSerializer, instance.composition)

    __composer_inventory_delete(instance)


# If pages have been added / removed from this item, catch them and re-index the item.
@receiver(m2m_changed, sender=Item.pages.through)
def index_item_page_relationships(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ('post_add', 'post_remove'):
        solr_index(ItemSearchSerializer, instance)


