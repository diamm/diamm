from diamm.models.migrate.legacy_image import LegacyImage
from diamm.models.migrate.legacy_item_image import LegacyItemImage
from diamm.models.migrate.legacy_secondary_image import LegacySecondaryImage
from diamm.models.data.image import Image
from diamm.models.data.image_type import ImageType
from diamm.models.data.image_note import ImageNote
from diamm.models.data.page_condition import PageCondition
from diamm.models.data.item import Item
from diamm.models.data.item_note import ItemNote
from blessings import Terminal

term = Terminal()


def empty_image():
    print(term.magenta("\tEmptying Image table"))
    Image.objects.all().delete()







def migrate_image(entry):
    print(term.green("\tMigrating primary image with ID {0}".format(entry.pk)))
    imtype = ImageType.objects.get(pk=ImageType.PRIMARY)
    filename = __determine_filename(entry)

    d = {
        "type": imtype,
        "filename": filename,
        "legacy_id": "legacy_image.{0}".format(int(entry.pk)),
        "photographer": entry.photographer,
        # "serial": entry.serial,
        "folio": entry.folio
    }

    im = Image(**d)
    im.save()

    if entry.vrevaluation:
        conditions = __determine_image_conditions(entry)
        im.conditions.add(*conditions)
        im.save()

    notes = (
        (ImageNote.CAPTURE_CONDITIONS, entry.captureconditions),
        (ImageNote.CAPTURE_DEVICE, entry.capturedevice),
        (ImageNote.FOCUS, entry.focus),
        (ImageNote.GAMMA, entry.gamma)
    )
    for n in notes:
        if n[1]:
            d = {
                "image": im,
                "note": n[1],
                "type": n[0]
            }
            imn = ImageNote(**d)
            imn.save()


def attach_item_to_image(entry):
    print(term.green("\tAttaching item {0} to image {1}".format(entry.itemkey, entry.imagekey)))
    item_pk = entry.itemkey
    item = Item.objects.get(pk=item_pk)
    image_pk = entry.imagekey
    image = Image.objects.get(legacy_id="legacy_image.{0}".format(int(image_pk)))

    image.items.add(item)
    image.save()



# nb: must be run after attaching the primary images to the items since this needs to look
# up the item from the primary image.
def migrate_secondary_image(entry):
    print(term.green("\tMigrating secondary image with ID {0}".format(entry.pk)))

    exists = Image.objects.filter(legacy_id="legacy_secondary_image.{0}".format(int(entry.pk)))
    if exists:
        print(term.red("\t\tDeleting existing secondary image ID {0}".format(entry.pk)))
        exists.delete()

    image = Image.objects.get(legacy_id="legacy_image.{0}".format(int(entry.imagekey)))
    items = image.items.all()
    type_pk = __determine_image_type(entry)
    type = ImageType.objects.get(pk=type_pk)

    d = {
        "legacy_id": "legacy_secondary_image.{0}".format(int(entry.pk)),
        "type": type,
        "caption": entry.caption,
        "filename": entry.filename,
        "folio": image.folio
    }
    im = Image(**d)
    im.save()

    im.items.add(*items)
    im.save()


def migrate():
    print(term.blue("Migrating Images"))
    empty_image()
    for entry in LegacyImage.objects.all():
        migrate_image(entry)

    for entry in LegacyItemImage.objects.all():
        attach_item_to_image(entry)

    for entry in LegacySecondaryImage.objects.all():
        migrate_secondary_image(entry)

    print(term.blue("Done migrating Images"))
