from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from diamm.models.data.person import Person
from diamm.serializers.search.person import PersonSearchSerializer
from diamm.helpers.solr_helpers import solr_delete, solr_index


@receiver(post_save, sender=Person)
def index_person(sender, instance, created, **kwargs):
    solr_index(PersonSearchSerializer, instance)


@receiver(post_delete, sender=Person)
def delete_person(sender, instance, **kwargs):
    solr_delete(instance)
