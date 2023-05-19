from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.models.data.image import Image
from diamm.models.data.page import Page
from diamm.serializers.search.page import PageSearchSerializer


# When an image record is saved we need to re-index the entire page since
# images are indexed as children of pages.
@receiver(post_save, sender=Image)
def index_image(sender, instance, created, **kwargs):
    # delete the page instance. It will be re-added when we index the page.
    solr_delete(instance)
    if instance.page:
        solr_index(PageSearchSerializer, instance.page)


@receiver(post_save, sender=Page)
def index_page(sender, instance, created, **kwargs):
    solr_index(PageSearchSerializer, instance)


@receiver(post_delete, sender=Image)
def delete_image(sender, instance, **kwargs):
    solr_delete(instance)


@receiver(post_delete, sender=Page)
def delete_page(sender, instance, **kwargs):
    solr_delete(instance)
