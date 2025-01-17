import asyncio
import re
import sys
from typing import Optional

import aiohttp
import blessings
import ujson
from django.core.management import BaseCommand

from diamm.helpers.iiif import PARSE_IIIF_URL, fetch_iiif_image_json
from diamm.models import Image, ImageType, Page, Source, SourceManifest

term = blessings.Terminal()
# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


IIIF_V3_CONTEXT = "http://iiif.io/api/presentation/3/context.json"
IIIF_V2_CONTEXT = "http://iiif.io/api/presentation/2/context.json"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("source_key", type=int)
        parser.add_argument("manifest_url", type=str)
        parser.add_argument(
            "-d",
            "--dry",
            dest="dry_run",
            action="store_true",
            default=False,
            help="Dry run.",
        )
        parser.add_argument(
            "-a",
            "--accept",
            dest="accept_header",
            help="Specific accept header to pass.",
        )

    def handle(self, *args, **kwargs):
        print("Running...")
        asyncio.run(self.async_handle(*args, **kwargs))

    async def async_handle(self, *args, **kwargs):
        source_key: str = kwargs["source_key"]
        manifest_url: str = kwargs["manifest_url"]
        dry_run: bool = kwargs["dry_run"]
        accept_header: str = kwargs["accept_header"]

        try:
            source_record = await Source.objects.aget(id=source_key)
        except Source.DoesNotExist:
            print(term.red(f"Source {source_key} does not exist."))
            sys.exit(1)

        if await source_record.pages.aexists():
            print(term.red(f"Source {source_key} already has pages attached."))
            sys.exit(1)

        manifest_exists: bool = await SourceManifest.objects.filter(
            manifest_url=manifest_url
        ).aexists()
        if manifest_exists:
            print(term.red(f"Manifest {manifest_url} already exists!"))
            sys.exit(1)

        out_headers = {}
        if accept_header:
            out_headers["Accept"] = accept_header

        print(term.blue(f"Fetching manifest {manifest_url}"))
        async with aiohttp.ClientSession(headers=out_headers) as session:
            async with session.get(manifest_url) as req:
                print("Inside request")
                if 200 <= req.status < 400:
                    manifest_json = await req.json()
                else:
                    print(term.red(f"Could not retrieve {manifest_url}"))
                    sys.exit(1)

        if "@context" not in manifest_json:
            print(term.red("No context in the manifest."))
            sys.exit(1)

        manifest_context: str = manifest_json["@context"]
        if manifest_context == IIIF_V3_CONTEXT:
            manifest_version = 3
        elif manifest_context == IIIF_V2_CONTEXT:
            manifest_version = 2
        else:
            print(term.red("Could not determine IIIF version."))
            sys.exit(1)

        print(term.blue(f"Found a IIIFv{manifest_version} manifest"))
        if not dry_run:
            sm = SourceManifest(
                **{
                    "source": source_record,
                    "manifest_url": manifest_url,
                    "iiif_version": manifest_version,
                }
            )
            await sm.asave()
        else:
            print(term.blue("Dry run. Skipped saving source manifest."))

        manifest_canvases: list
        if manifest_version == 3:
            manifest_canvases = get_iiif_v3_canvases(manifest_json)
        else:
            manifest_canvases = get_iiif_v2_canvases(manifest_json)

        imtype = await ImageType.objects.aget(pk=ImageType.PRIMARY)

        for cnum, canvas in enumerate(manifest_canvases, start=1):
            print(term.blue(f"Processing canvas {cnum}"))
            canvas_id: Optional[str] = get_canvas_id(canvas)
            if not canvas_id:
                print(term.yellow(f"Could not determine id field for {canvas}"))
                continue

            canvas_label: str = get_canvas_label(canvas, cnum, manifest_version)

            print(term.blue("\tCreating a new page record"))
            p = {
                "source": source_record,
                "numeration": canvas_label,
                "sort_order": cnum,
                "page_type": Page.PAGE,
                "iiif_canvas_uri": canvas_id,
                "external": True,
            }

            new_page: Optional[Page] = None
            if not dry_run:
                new_page = Page(**p)
                await new_page.asave()

            iiif_image_uri = get_iiif_image_uri(canvas, manifest_version)
            print(term.blue("\tFetching IIIF Image Info.json"))
            info_json: Optional[dict] = fetch_iiif_image_json(iiif_image_uri)
            if not info_json:
                print(term.yellow(f"\tCould not retrieve info for {iiif_image_uri}"))
                continue

            info_req = re.sub(PARSE_IIIF_URL, r"\1/info.json", iiif_image_uri)
            print(term.blue("\tCreating a new page image."))
            im = {
                "page": new_page,
                "type": imtype,
                "location": info_req,
                "external": True,
                "public": True,
                "iiif_response_cache": ujson.dumps(info_json),
            }

            new_image: Optional[Image] = None
            if not dry_run:
                print(term.cyan("\tActually saving image"))
                new_image = Image(**im)
                await new_image.asave()

            print(term.cyan("Done!"))


def get_iiif_v2_canvases(manifest: dict) -> Optional[list]:
    list_of_sequences: list = manifest.get("sequences", [])
    if not list_of_sequences:
        return None

    list_of_canvases: list = list_of_sequences[0].get("canvases", [])
    if not list_of_canvases:
        return None

    return list_of_canvases


def get_iiif_v3_canvases(manifest: dict) -> Optional[list]:
    if "items" not in manifest:
        return None

    # will return a list or "None" if it fails for some reason.
    return manifest.get("items")


def get_canvas_id(canvas: dict) -> Optional[str]:
    if "id" in canvas:
        return canvas["id"]
    elif "@id" in canvas:
        return canvas["@id"]
    else:
        return None


def get_canvas_label(canvas: dict, cnum: int, manifest_version: int) -> Optional[str]:
    if "label" not in canvas:
        # provide a supplied label
        return f"[{cnum}]"

    canvas_label = canvas["label"]
    if isinstance(canvas_label, dict):
        if "en" in canvas_label:
            return canvas_label["en"][0]
        elif "none" in canvas_label:
            return canvas_label["none"][0]
        elif "fr" in canvas_label:
            return canvas_label["fr"][0]
        elif "de" in canvas_label:
            return canvas_label["de"][0]
        else:
            print(term.yellow(f"Could not get label for dict: {canvas_label}."))
            return str(canvas_label)
    elif isinstance(canvas_label, list):
        if len(canvas_label) > 0:
            return canvas_label[0]
        else:
            print(term.yellow(f"Could not get label for list: {canvas_label}."))
            return str(canvas_label)
    elif isinstance(canvas_label, str):
        return canvas_label
    else:
        print(
            term.yellow(
                f"Could not determine type of canvas label for {canvas_label}. Supplying one."
            )
        )
        return f"[{cnum}]"


def get_iiif_image_uri(canvas: dict, manifest_version: int) -> Optional[str]:
    if manifest_version == 2:
        image: list = canvas.get("images", [])
        if len(image) == 0:
            print(term.yellow(f"Could not get image for {canvas}"))
            return None
        image_block = image[0]
        if "resource" not in image_block:
            print(term.yellow(f"'resource' not in image block for {canvas}"))
            return None

        image_uri: str = image_block["resource"]["@id"]
        return image_uri

    elif manifest_version == 3:
        image: list = canvas.get("items", [])
        if len(image) == 0:
            print(term.yellow(f"Could not get image for {canvas}"))
            return None
        image_block = image[0]["items"][0]["body"]
        image_uri: str = image_block["id"]
        return image_uri
