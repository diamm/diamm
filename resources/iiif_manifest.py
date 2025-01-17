import argparse
import copy
import csv
import json
import logging
import os
import sys
from typing import Optional

log = logging.getLogger(__name__)


IIIF_MANIFEST_TEMPLATE = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": "",
    "@type": "sc:Manifest",
    "label": "",
    "description": "",
    "attribution": "<span>IIIF Hosting provided by the Digital Image Archive of Medieval Music.</span>",
    "viewingHint": "paged",
    "viewingDirection": "left-to-right",
    "sequences": [
        {
            "@id": "https://iiif.bodleian.ox.ac.uk/iiif/sequence/8ed09252-7a96-46ec-8973-fa1db144b477_default.json",
            "@type": "sc:Sequence",
            "label": "Default",
            "canvases": [],
        }
    ],
}

IIIF_CANVAS_TEMPLATE = {
    "@id": "https://iiif.bodleian.ox.ac.uk/iiif/canvas/96767885-6497-4bc3-b9f2-cdb37c42214d.json",
    "@type": "sc:Canvas",
    "label": "",
    "width": 2628,
    "height": 4056,
    "images": [
        {
            "@id": "https://iiif.bodleian.ox.ac.uk/iiif/annotation/96767885-6497-4bc3-b9f2-cdb37c42214d.json",
            "@type": "oa:Annotation",
            "motivation": "sc:painting",
            "on": "https://iiif.bodleian.ox.ac.uk/iiif/canvas/96767885-6497-4bc3-b9f2-cdb37c42214d.json",
            "resource": {
                "@id": "https://iiif.bodleian.ox.ac.uk/iiif/image/96767885-6497-4bc3-b9f2-cdb37c42214d",
                "@type": "dctypes:Image",
                "format": "image/jpeg",
                "width": 2628,
                "height": 4056,
                "service": {
                    "@id": "https://iiif.bodleian.ox.ac.uk/iiif/image/96767885-6497-4bc3-b9f2-cdb37c42214d",
                    "@context": "http://iiif.io/api/image/2/context.json",
                    "profile": "http://iiif.io/api/image/2/level1.json",
                },
            },
        }
    ],
}

IIIF_MANIFEST_ID_TMPL = "https://iiif.diamm.net/manifests/{manifest_path}"
IIIF_CANVAS_ID_TMPL = "https://iiif.diamm.net/canvases/{image_ident}"
IIIF_IMAGE_ID_TMPL = "https://iiif.diamm.net/images/{image_path}"
IIIF_ANNOTATION_ID_TMPL = "https://iiif.diamm.net/annotations/{image_ident}"
IIIF_SEQUENCE_ID_TMPL = "https://iiif.diamm.net/sequences/{mss_label}_default"


def get_dimensions(img_path: str) -> tuple[int, int] | None:
    """
    Returns a tuple (w, h) of an image with a given ID. This image must be in a
    pairwise tree in the same silo as the master record. Reads the w/h data directly
    from the JPEG 2000 header.

    :param img_path: a path to a JPEG 2000 image
    :return: A tuple containing the width and height of the image. 0,0 if there was a problem indexing the file
    """
    log.debug("Getting dimensions for %s", img_path)
    width: int = 0
    height: int = 0

    try:
        f = open(img_path, "rb")
    except FileNotFoundError:
        # Log this as a debug message, since we will catch this up the call stack and also include the master file
        # from which we found it.
        log.debug("%s was not found.", img_path)
        return width, height

    d = f.read(200)
    start_header = d.find(b"ihdr")

    if start_header == -1:
        log.error(
            "Header error with %s. Malformed JPEG 2000 image. Setting to 0, 0", img_path
        )
        return width, height

    hs = start_header + 4
    ws = start_header + 8
    try:
        height = d[hs] * 256**3 + d[hs + 1] * 256**2 + d[hs + 2] * 256 + d[hs + 3]
        width = d[ws] * 256**3 + d[ws + 1] * 256**2 + d[ws + 2] * 256 + d[ws + 3]
    except IndexError:
        # If there was a problem reading the JP2, allow the process to continue. It should be easy to identify
        # failed images later as they will be the ones with w,h as 0,0.
        log.error(
            "Index error with %s. Could not find width and height. Setting to 0, 0.",
            img_path,
        )
    finally:
        f.close()

    return width, height


def compile_images(image_root, csvfile) -> Optional[tuple[str, list]]:
    # base_directory = os.path.basename(image_directory)
    # fieldnames = ("SKIP", "filepfx", "filesfx", "label")
    # fieldnames = ("path",)
    all_images = []
    base_directory = None
    manifest_label = None
    with open(csvfile) as imagelist:
        reader = csv.DictReader(imagelist)
        for row in reader:
            image_path: Optional[str] = row.get("path")
            if not image_path:
                log.error(
                    "Uh oh, something went wrong with %s. Bailing until it's fixed.",
                    row,
                )
                return None

            folder, img = image_path.split("/")
            if not base_directory:
                base_directory = os.path.basename(folder)

            if not manifest_label:
                manifest_label = folder

            prefix, suffix = img.rsplit(".", 1)
            base, label = prefix.rsplit("_", 1)
            # print(folder, base, label, suffix)

            full_image_path = os.path.join(image_root, f"{image_path}")
            image_ident = os.path.join(base_directory, f"{prefix}")
            image_entry = os.path.join(base_directory, f"{img}")

            print(full_image_path)
            if not os.path.exists(full_image_path):
                log.error(
                    "Image does not exist! %s. Bailing until it's fixed.",
                    full_image_path,
                )
                return None

            width, height = get_dimensions(full_image_path)

            d = {
                "image_path": full_image_path,
                "image_ident": image_ident,
                "image_entry": image_entry,
                "width": width,
                "height": height,
                "label": label,
            }
            all_images.append(d)

    return manifest_label, all_images


def main(options) -> bool:
    csvfile = options.csvfile
    image_root = options.imageroot
    # mss_label = os.path.basename(image_root)
    new_manifest = copy.deepcopy(IIIF_MANIFEST_TEMPLATE)
    parsed_output = compile_images(image_root, csvfile)
    if parsed_output is None:
        return False

    mss_label, compiled = parsed_output

    manifest_path = os.path.join(mss_label, "manifest.json")
    manifest_id = IIIF_MANIFEST_ID_TMPL.format(manifest_path=manifest_path)
    new_manifest["@id"] = manifest_id
    new_manifest["label"] = mss_label
    new_manifest["description"] = mss_label
    new_manifest["sequences"][0]["@id"] = IIIF_SEQUENCE_ID_TMPL.format(
        mss_label=mss_label
    )

    for img in compiled:
        new_canvas = copy.deepcopy(IIIF_CANVAS_TEMPLATE)
        width = img["width"]
        height = img["height"]

        new_canvas["width"] = width
        new_canvas["height"] = height
        new_canvas["@id"] = IIIF_CANVAS_ID_TMPL.format(image_ident=img["image_ident"])
        new_canvas["label"] = img["label"]
        new_canvas["images"][0]["@id"] = IIIF_ANNOTATION_ID_TMPL.format(
            image_ident=img["image_ident"]
        )
        new_canvas["images"][0]["on"] = IIIF_CANVAS_ID_TMPL.format(
            image_ident=img["image_ident"]
        )
        new_canvas["images"][0]["resource"]["@id"] = IIIF_IMAGE_ID_TMPL.format(
            image_path=img["image_entry"]
        )
        new_canvas["images"][0]["resource"]["service"]["@id"] = (
            IIIF_IMAGE_ID_TMPL.format(image_path=img["image_entry"])
        )

        new_manifest["sequences"][0]["canvases"].append(new_canvas)

    if not os.path.exists(mss_label):
        os.mkdir(mss_label)

    with open(manifest_path, "w") as mfile:
        json.dump(new_manifest, mfile, indent=4)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csvfile")
    parser.add_argument("imageroot")

    in_args = parser.parse_args()

    success: bool = main(in_args)
    if not success:
        sys.exit(1)

    sys.exit()
