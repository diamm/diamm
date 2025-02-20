import argparse
import copy
import csv
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


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


def compile_images(image_root) -> list[dict]:
    all_images = []
    image_files = Path(image_root).glob("**/*.jpx")
    for ifile in image_files:
        width, height = get_dimensions(ifile)
        all_images.append({"width": width, "height": height, "filename": str(ifile)})
    return all_images


def main(options) -> bool:
    image_data = compile_images(options.imageroot)
    with open("image-data.csv", "w") as csvfile:
        fieldnames = ["width", "height", "filename"]
        # noinspection PyTypeChecker
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("imageroot")

    in_args = parser.parse_args()

    success: bool = main(in_args)
    if not success:
        sys.exit(1)

    sys.exit()
