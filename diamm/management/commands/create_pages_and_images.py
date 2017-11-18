"""
Used to create Page and Image entries for new sources.
"""
import os
import sys
import glob
import re
import logging
from django.core.management import BaseCommand
from django.conf import settings
import blessings
import requests
import ujson
from urllib.parse import urljoin
from diamm.models.data.source import Source
from diamm.models.data.page import Page
from diamm.models.data.image import Image
from diamm.models.data.image_type import ImageType

term = blessings.Terminal()
logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG)
log = logging.getLogger(__name__)

# Names which do not follow the foliation standard have to be special-cased.
# The keys will be used in a matching regex below, and the matching value will then be
# used as the page label.
NON_FOLIATED_NAMES = {
    "backcover": "Back cover",
    "frontcover_1": "Front cover (1)",
    "frontfly1r": "Front fly 1r",
    "frontfly1v": "Front fly 1v",
    "frontfly2r": "Front fly 2r",
    "frontfly2v": "Front fly 2v",
    "insidebackcover": "Inside back cover",
    "insidefrontcover": "Inside front cover",
    "rearfly1r": "Rear fly 1r",
    "rearfly1v": "Rear fly 1v",
    "rearfly2r": "Rear fly 2r",
    "rearfly2v": "Rear fly 2v",
    "stitchingr_w": "Stitching recto",
    "back": "Back",
    "bkboard": "Back board",
    "bkfly_verso": "Back fly verso",
    "bkfly_w": "Back fly watermark",
    "bkfly": "Back fly",
    "frfly": "Front fly",
    "front": "Front",
    "frontflyverso": "Front fly verso",
    "insidefrontboard": "Inside front board",
    "spine": "Spine",
    "test": "Test"
}

TYPE_MAP = {
    None: ImageType.objects.get(pk=ImageType.PRIMARY),
    "_w": ImageType.objects.get(pk=ImageType.WATERMARK),
    "_a": ImageType.objects.get(pk=ImageType.ALT_SHOT)
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('sourcekey', type=int)
        parser.add_argument('foldername', type=str)
        parser.add_argument('-d',
                            "--dry",
                            dest="dry_run",
                            action="store_true",
                            default=False,
                            help="Dry run; don't actually save anything.")

    def handle(self, *args, **options):
        """
        Automatically creates page and image records for sources that do not have them already.

        If image types are "special" -- that is, if they have extensions after the folio number like "_w" (watermark)
        then creation of a page record for that image will not happen. Instead, an attempt will be made to attach
        it to a "regular" page.

        Any non-foliated pages (covers, etc.) will be added as a regular page; it is then up to the editor to
        go in and manually fix it after.

        :param args:
        :param options:
        :return:
        """
        sourcekey = options['sourcekey']
        foldername = options['foldername']
        dryrun = options['dry_run']

        if dryrun:
            log.info(term.yellow("DRY RUN. Changes will not be committed."))

        folderpath = os.path.join("/data", "images", foldername)
        if not os.path.exists(folderpath):
            log.error(term.red("Folder {0} does not exist. Exiting.".format(foldername)))
            sys.exit(-1)

        try:
            src = Source.objects.get(pk=sourcekey)
        except Source.DoesNotExist:
            log.error(term.red("Source {0} does not exist. Exiting.".format(sourcekey)))
            sys.exit(-1)

        # Check whether source has pages attached already
        num_pages = src.pages.count()
        if num_pages > 0:
            log.error(term.red("Source already has {0} page records. This should only be run on sources with no existing page records."))
            sys.exit(-1)

        # Check how many images are in the images folder.
        files = sorted(glob.glob(os.path.join(folderpath, "*.jpx")))

        if len(files) == 0:
            log.error(term.red("There were no JPX files in {0}. Exiting.".format(foldername)))
            sys.exit(-1)

        # Try to parse the filename for info.
        page_name_regex = re.compile(r"(?P<sig>.*)_(?P<pname>(\d{3}[r|v])|(" + "|".join(NON_FOLIATED_NAMES.keys()) + r"))(?P<spctype>_w)?(?P<ext>.jpx)")

        for order, imagepath in enumerate(files):
            log.info(term.magenta("------- New image {0} --------".format(imagepath)))
            image_name = os.path.basename(imagepath)

            # Try to retrieve the image.
            loc = "https://{0}/iiif/image/{1}/{2}".format(settings.HOSTNAME, foldername, image_name)
            url = urljoin(loc + '/', "info.json")

            log.info(term.green("Retrieving {0}".format(url)))
            r = requests.get(url, headers={
                "referer": "https://{0}".format(settings.HOSTNAME),
                "X-DIAMM": settings.DIAMM_IMAGE_KEY
            })

            iiif_resp = None
            if 200 <= r.status_code < 300:
                log.info(term.green("Received a success response from info.json retrieval"))
                j = r.json()
                iiif_resp = ujson.dumps(j)
            elif r.status_code == 404:
                log.warning(term.yellow("404 not found for {0}".format(loc)))
                log.warning(term.yellow("Skipping."))
                continue

            if iiif_resp is None:
                log.warning(term.yellow("No valid IIIF image response. Skipping."))
                continue

            re_match = re.match(page_name_regex, image_name)
            if not re_match:
                log.warning(term.yellow("No matches found for {0}. It will be skipped.".format(image_name)))
                continue

            pname = re_match.group("pname")
            special_type = re_match.group("spctype")

            log.debug(term.green("Parsing filename: Page name: {pname}, Special type: {spctype}".format(pname=pname, spctype=special_type)))

            # Try to get the special page names; if None, use the name from the filename.
            page_name = NON_FOLIATED_NAMES.get(pname, None)
            if not page_name:
                page_name = pname

            if not special_type:
                log.info(term.green("Creating a regular page with label {0}".format(page_name)))
                # Create a page record.
                p = {
                    'source': src,
                    'numeration': page_name,
                    'sort_order': order,
                    'page_type': Page.PAGE
                }
                if not dryrun:
                    pg = Page(**p)
                    pg.save()
            else:
                # Try to find a previously-saved page
                log.info(term.green("Found a special image; trying to retrieve a page record for it."))
                try:
                    pg = Page.objects.filter(numeration=page_name).first()
                except Page.DoesNotExist:
                    print(term.yellow("Could not find an ordinary page for label {0}".format(page_name)))
                    print(term.yellow("Special image {0} could not be attached to a page.".format(image_name)))
                    continue

            # Create an image record
            imtype = TYPE_MAP.get(special_type)
            log.info(term.green("Creating an image record."))

            if dryrun:
                pg = None

            im = {
                "page": pg,
                "type": imtype,
                "location": loc,
                "public": True,
                "iiif_response_cache": iiif_resp
            }

            if not dryrun:
                img = Image(**im)
                img.save()

        log.info("Done adding pages and images.")
