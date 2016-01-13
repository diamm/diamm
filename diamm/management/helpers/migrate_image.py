from diamm.models.migrate.legacy_image import LegacyImage
from diamm.models.migrate.legacy_item_image import LegacyItemImage
from diamm.models.migrate.legacy_secondary_image import LegacySecondaryImage
from diamm.models.data.image import Image
from diamm.models.data.image_type import ImageType
from diamm.models.data.image_note import ImageNote
from diamm.models.data.image_page_condition import ImagePageCondition
from diamm.models.data.item import Item
from diamm.models.data.item_note import ItemNote
from blessings import Terminal

term = Terminal()


def empty_image():
    print(term.magenta("\tEmptying Image table"))
    Image.objects.all().delete()


def __determine_image_conditions(entry):
    entries = entry.vrevaluation.split("\r")
    out = []
    for e in entries:
        if e == "good":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.GOOD))
        elif e == "mild tweaking":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.MILD_TWEAKING))
        elif e == "moderate":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.MODERATE))
        elif e == "water stained":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.WATER_STAINED))
        elif e == "show-through":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.SHOW_THROUGH))
        elif e == "burn-through":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.BURN_THROUGH))
        elif e == "poor":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.POOR))
        elif e == "piss poor":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.VERY_POOR))
        elif e == "requires enhancement":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.REQUIRES_ENHANCEMENT))
        elif e == "badly damaged":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.BADLY_DAMAGED))
        elif e == "offset":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.OFFSET))
        elif e == "illegible":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.ILLEGIBLE))
        elif e == "cropped":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.CROPPED))
        elif e == "requires UV":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.REQUIRES_UV))
        elif e == "palimpsest":
            out.append(ImagePageCondition.objects.get(pk=ImagePageCondition.PALIMPSEST))
        else:
            print(term.red("Could not determine condition for type: {0}".format(e)))
    return out


def __determine_image_type(entry):
    c = entry.caption
    if c in ("colour UV image", "Colour UV", "original colour UV image", "colour UV image - may not exist",
             "colour UV image, reversed", "colour UV image, level adjusted", "UV (colour)", "UV (Colour)",
             "colour UV", "f. 1 colour UV", "f. 4v colour UV", "Enhanced colour UV", "enhanced colour UV image",
             "Original RGB with enhanced UV (D Fallows)", "UV exposure 1", "UV exposure 2", "UV exposure 3",
             "UV exposure 4", "UV exposure 5", "UV exposure 6", "UV exposure 7", "UV exposure 8"):
        return ImageType.COLOUR_UV
    elif c in ("b/w UV image", "black and white UV image", "b/w UV image, levels adjusted", "black and whie UV image",
               "UV image", "grayscale UV image", "grayscale UV image with blue filter", "grayscale UV image with high-contrast blue filter",
               "b/w high-contrast UV", "high-contrast b/w UV image", "detail UV"):
        return ImageType.GRAYSCALE_UV
    elif c in ("detail of page showing pasted capital", "detail of bottom edge", "detail of page",
               "detail of page with different colour balance", "detail of page showing scribe's blood",
               "detail of pasted capital; watermark also visible", "detail of page showing slip pasted in",
               "detail", "lower edge", "detail of illumination", "detail of fragment", "detail: 1v", "detail enhanced",
               "gutter margin", "gutter image"):
        return ImageType.DETAIL
    elif c in ("alternative scan settings", "second shot", "alternative shot", "colour target",
               "full page photgraphed using transmissive light", "image supplied by library", "reproduction from older microfilm"):
        return ImageType.ALT_SHOT
    elif c in ("alternative focus/lighting", "alternative focus", None):
        return ImageType.ALT_FOCUS
    elif c in ("different exposure",):
        return ImageType.ALT_EXPOSURE
    elif c in ("Digitally enhanced image (GV)", "Digitally enhanced image", "digitally enhanced image", "Digitally enhanced show-through text higlighted (GV)",
               "enhanced monochrome (JCM)", "digitally enhanced (JCM)", "Mirror image and enhanced (JCM)", "enhanced (JCM)", "Digitally enhanced (JCM)",
               "enhanced monochrome", "flipped and enhanced", "Digitally enhanced image (JCM)", "Digitally enhanced image (E Anstice)",
               "flipped and darkened", "flipped and colour adjusted", "flipped and colour-adjusted", "flipped"):
        return ImageType.DIGITALLY_ENHANCED
    elif c in ("Digitally restored image (GV)", "digitally restored, b/w (M S Cuthbert)"):
        return ImageType.DIGITALLY_RESTORED
    elif c in ("Watermark", "watermark"):
        return ImageType.WATERMARK
    elif c in ("light levels adjusted, text darkened", "light levels adjusted"):
        return ImageType.LEVEL_ADJUST
    elif c in ("with raking light", "raking light"):
        return ImageType.RAKING_LIGHT
    elif c in ("Infra-red exposure 1", "infra-red exposure 1", "Infra-red exposure 2", "infra-red exposure 2", "Infra-red exposure 3", "infra-red exposure 3",
               "Infra-red exposure 4", "infra-red exposure 4", "infra-red exposure 5", "Infra-red exposure 5", "Infra-red exposure 6", "infra-red exposure 6"):
        return ImageType.INFRARED
    else:
        print(term.red("\tCould not determine imagetype for {0}".format(c)))


def __determine_filename(entry):
    if entry.archivedfilename:
        return entry.archivedfilename
    elif entry.filename and entry.filename not in ('not photographed', 'applytolibrary'):
        return entry.filename
    else:
        print(term.red("\tCould not determine filename for image {0}".format(entry.pk)))
        return None

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

    notes = (
        (ItemNote.I_DECORATION_COLOUR, entry.decorationcolour),
        (ItemNote.I_DECORATION_STYLE, entry.decorationstyle),
        (ItemNote.I_INITIAL, entry.initial),
        (ItemNote.I_INITIAL_COLOUR, entry.initialcolour)
    )
    for n in notes:
        if n[1]:
            print(term.green("\t\tMigrating notes to the item level."))
            d = {
                'type': n[0],
                'note': n[1],
                'item': item
            }
            itmn = ItemNote(**d)
            itmn.save()


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
