from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from diamm.models.data.item import Item
from diamm.models.data.page import Page
from diamm.models.data.source import Source


@receiver(post_save, sender=Source)
def downgrade_dependent_virtual_source_rights(sender, instance, **kwargs):
    """A donor becoming stricter immediately makes all dependent copies stricter."""
    dependent_ids = Page.objects.filter(
        copied_from__source=instance,
        source__is_virtual=True,
    ).values_list("source_id", flat=True)
    updates = {}
    if not instance.public_images:
        updates["public_images"] = False
    if not instance.open_images:
        updates["open_images"] = False
    if updates:
        Source.objects.filter(pk__in=dependent_ids).update(**updates)


@receiver(pre_delete, sender=Page)
def remember_copied_items_for_deleted_page(sender, instance, **kwargs):
    instance._copied_item_ids = list(
        instance.items.filter(copied_from__isnull=False).values_list("pk", flat=True)
    )


@receiver(post_delete, sender=Page)
def delete_orphaned_copied_items(sender, instance, **kwargs):
    item_ids = getattr(instance, "_copied_item_ids", ())
    if item_ids:
        Item.objects.filter(pk__in=item_ids, pages__isnull=True).delete()
