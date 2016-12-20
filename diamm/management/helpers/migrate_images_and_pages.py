from django.db.models import Q
from diamm.models.data.source import Source
from diamm.models.data.image import Image
from diamm.models.data.item import Item
from diamm.models.data.image_type import ImageType
from diamm.models.data.page import Page
from diamm.models.data.page_condition import PageCondition
from diamm.models.data.page_note import PageNote
from diamm.models.migrate.legacy_image import LegacyImage
from diamm.models.migrate.legacy_secondary_image import LegacySecondaryImage
from diamm.models.migrate.legacy_item_image import LegacyItemImage
from diamm.management.helpers.utilities import convert_yn_to_boolean, remove_leading_zeroes
from blessings import Terminal

term = Terminal()


def empty_page_and_image():
    print(term.blue("\tDeleting Images"))
    Image.objects.all().delete()
    print(term.blue("\tDeleting Pages"))
    Page.objects.all().delete()


def __determine_page_conditions(entry):
    entries = entry.vrevaluation.split("\r")
    out = []
    for e in entries:
        if e == "good":
            out.append(PageCondition.objects.get(pk=PageCondition.GOOD))
        elif e == "mild tweaking":
            out.append(PageCondition.objects.get(pk=PageCondition.MILD_TWEAKING))
        elif e == "moderate":
            out.append(PageCondition.objects.get(pk=PageCondition.MODERATE))
        elif e == "water stained":
            out.append(PageCondition.objects.get(pk=PageCondition.WATER_STAINED))
        elif e == "show-through":
            out.append(PageCondition.objects.get(pk=PageCondition.SHOW_THROUGH))
        elif e == "burn-through":
            out.append(PageCondition.objects.get(pk=PageCondition.BURN_THROUGH))
        elif e == "poor":
            out.append(PageCondition.objects.get(pk=PageCondition.POOR))
        elif e == "piss poor":
            out.append(PageCondition.objects.get(pk=PageCondition.VERY_POOR))
        elif e == "requires enhancement":
            out.append(PageCondition.objects.get(pk=PageCondition.REQUIRES_ENHANCEMENT))
        elif e == "badly damaged":
            out.append(PageCondition.objects.get(pk=PageCondition.BADLY_DAMAGED))
        elif e == "offset":
            out.append(PageCondition.objects.get(pk=PageCondition.OFFSET))
        elif e == "illegible":
            out.append(PageCondition.objects.get(pk=PageCondition.ILLEGIBLE))
        elif e == "cropped":
            out.append(PageCondition.objects.get(pk=PageCondition.CROPPED))
        elif e == "requires UV":
            out.append(PageCondition.objects.get(pk=PageCondition.REQUIRES_UV))
        elif e == "palimpsest":
            out.append(PageCondition.objects.get(pk=PageCondition.PALIMPSEST))
        else:
            print(term.red("Could not determine condition for type: {0}".format(e)))
    return out


def determine_image_type(entry):
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


def determine_filename(entry):
    if entry.filename and entry.filename not in ('not photographed', 'not_photographed', 'notphotographed', 'applytolibrary', 'librarydigitized'):
        return entry.filename.strip()
    elif hasattr(entry, 'archivedfilename') and entry.archivedfilename is not None:
        return entry.archivedfilename.strip()
    elif hasattr(entry, 'archivefilename') and entry.archivefilename is not None:
        return entry.archivefilename.strip()
    else:
        print(term.red("\tCould not determine filename for image {0}".format(entry.pk)))
        return None


def convert_image(entry):
    print(term.green("\tMigrating image with ID {0} to a Page".format(entry.pk)))
    source = Source.objects.get(pk=int(entry.sourcekey))
    folio = entry.folio if entry.folio else "FIXMEFOLIO"

    d = {
        'numeration': remove_leading_zeroes(folio),
        'sort_order': entry.orderno,
        'source': source,
        'legacy_id': "legacy_image.{0}".format(entry.pk)
    }

    p = Page(**d)
    p.save()

    filename = determine_filename(entry)

    if filename:
        # create an image record.
        print(term.green("\t\tCreating an Image record for Image {0} ({1})".format(entry.pk, filename)))
        available = convert_yn_to_boolean(entry.availwebsite)
        imtype = ImageType.objects.get(pk=ImageType.PRIMARY)

        imd = {
            'page': p,
            'public': available,
            'type': imtype,
            'legacy_filename': filename,
            'legacy_id': 'legacy_image.{0}'.format(int(entry.pk))
        }

        im = Image(**imd)
        im.save()
    else:
        print(term.yellow("\t\tSkipping {0}".format(filename)))


def convert_secondary_image(entry):
    print(term.green("\tMigrating secondary image {0}".format(entry.pk)))
    filename = determine_filename(entry)
    if not filename:
        return None

    orig_image_pk = "legacy_image.{0}".format(int(entry.imagekey))
    try:
        orig_image = Image.objects.get(legacy_id=orig_image_pk)
    except Image.DoesNotExist:
        print(term.red("\t\tImage {0} does not exist. Skipping.".format(orig_image_pk)))
        return None

    page = orig_image.page
    imtype_pk = determine_image_type(entry)
    print(imtype_pk)

    imtype = ImageType.objects.get(pk=imtype_pk)

    imd = {
        "legacy_id": "legacy_secondary_image.{0}".format(int(entry.pk)),
        "legacy_filename": filename,
        "page": page,
        "type": imtype,
        "public": orig_image.public
    }
    im = Image(**imd)
    im.save()


def attach_item_to_page(entry):
    print(term.green("\tAttaching item {0} to image {1} (relationship {2})".format(entry.itemkey, entry.imagekey, entry.pk)))
    item_pk = int(entry.itemkey)

    # These items have an image attached to it, and they shouldn't really. Skip them.
    if item_pk in (92020, 71686):
        return None

    try:
        item = Item.objects.get(pk=item_pk)
    except Item.DoesNotExist:
        print(term.red("\t\tItem {0} Does not exist".format(item_pk)))
        return None

    image_pk = int(entry.imagekey)
    page = Page.objects.get(legacy_id="legacy_image.{0}".format(image_pk))

    item.pages.add(page)
    item.save()

    note_fields = (
        (PageNote.DECORATION_COLOUR, entry.decorationstyle),
        (PageNote.DECORATION_COLOUR, entry.decorationcolour),
        (PageNote.INITIAL, entry.initial),
        (PageNote.INITIAL_COLOUR, entry.initialcolour)
    )

    for nt in note_fields:
        if not nt[1]:
            continue

        d = {
            'type': nt[0],
            'note': nt[1],
            'page': page
        }
        pgn = PageNote(**d)
        pgn.save()


def migrate():
    print(term.green("Migrating Images and converting them to Pages"))
    empty_page_and_image()
    for entry in LegacyImage.objects.all():
        convert_image(entry)

    for entry in LegacySecondaryImage.objects.all():
        convert_secondary_image(entry)

    for entry in LegacyItemImage.objects.all():
        attach_item_to_page(entry)


def update_page_notes():
    PageNote.objects.all().delete()
    legacy_item_image = LegacyItemImage.objects.filter(Q(decorationstyle__isnull=False) | Q(decorationcolour__isnull=False) | Q(initial__isnull=False) | Q(initialcolour__isnull=False))

    for entry in legacy_item_image:
        print("Updating entry {0}".format(entry.pk))

        try:
            page = Page.objects.get(legacy_id="legacy_image.{0}".format(int(entry.imagekey)))
        except Page.DoesNotExist:
            print('page could not be found')
            continue

        note_fields = (
            (PageNote.DECORATION_COLOUR, entry.decorationstyle),
            (PageNote.DECORATION_COLOUR, entry.decorationcolour),
            (PageNote.INITIAL, entry.initial),
            (PageNote.INITIAL_COLOUR, entry.initialcolour)
        )

        for nt in note_fields:
            if not nt[1]:
                continue

            d = {
                'type': nt[0],
                'note': nt[1],
                'page': page
            }
            pgn = PageNote(**d)
            pgn.save()
