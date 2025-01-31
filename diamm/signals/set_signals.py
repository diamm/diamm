from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.models.data.set import Set
from diamm.serializers.search_old.set import SetSearchSerializer


@receiver(post_save, sender=Set)
def index_set(sender, instance, created, **kwargs):
    solr_index(SetSearchSerializer, instance)


@receiver(post_delete, sender=Set)
def delete_set(sender, instance, **kwargs):
    solr_delete(instance)
