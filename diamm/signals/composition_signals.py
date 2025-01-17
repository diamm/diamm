from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.models.data.composition import Composition
from diamm.serializers.search.composition import CompositionSearchSerializer


@receiver(post_save, sender=Composition)
def index_composition(sender, instance, created, **kwargs):
    solr_index(CompositionSearchSerializer, instance)


@receiver(post_delete, sender=Composition)
def delete_composition(sender, instance, **kwargs):
    solr_delete(instance)
