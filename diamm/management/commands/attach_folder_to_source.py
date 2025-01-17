import csv
import glob
import os
import re
import sys
from urllib.parse import urljoin

import blessings
import requests
import ujson
from django.conf import settings
from django.core.management.base import BaseCommand

from diamm.models.data.image import Image
from diamm.models.data.source import Source

term = blessings.Terminal()


def _check_input(imagename, filenames):
    while True:
        possible_default = re.sub(r"(Add\.|add)", "Add", imagename)
        possible_default = re.sub(r"\s", "_", possible_default)
        inp = input(f"Fix {imagename} ([{possible_default}]?): ")

        # Allow the user to choose to delete or keep this image without matching a filename. Use with caution.
        if inp in ("d", "k", "r"):
            return inp

        # Accept the default. This will still get checked against the list of available filenames.
        if not inp:
            inp = possible_default

        if inp not in filenames:
            print(term.red(f"{inp} is not in the list of filenames. Please try again."))
            continue
        else:
            break

    return inp


def preflight_checks(csvdata):
    passed = True
    for row in csvdata:
        folder = row["folder"]
        source = row["source_id"]
        print(term.blue(f"Checking {folder}..."))
        # check that the folder exists
        foldername = os.path.join("/data", "images", folder)
        if not os.path.exists(foldername):
            passed = False
            print(term.red(f"Folder {foldername} does not exist"))

        # check that the source exists
        try:
            source = Source.objects.get(pk=source)
        except Source.DoesNotExist:
            passed = False
            print(
                term.red(
                    f"Source {source} does not exist. Please check this entry and re-try"
                )
            )

        # get filenames in directory
        files = glob.glob(os.path.join(foldername, "*.jpx"))
        fns = [os.path.splitext(os.path.relpath(p, foldername))[0] for p in files]
        images = source.pages.values_list(
            "images__pk", "images__legacy_filename", "numeration"
        )
        file_errors = []

        for image in images:
            if image[1] not in fns:
                passed = False
                print(
                    term.red(
                        f"NOT_FOUND:\tImage {term.white}{image[1]}{term.red} (pk {image[0]}) in the database is not in the list of available files."
                    )
                )
                file_errors.append(image)
            elif re.match(r".*\s+.*", image[1]):
                passed = False
                print(
                    term.red(
                        f"SPACES_IN_NAME:\tThere were spaces in Image {term.white}{image[1]}{term.red} (pk {image[0]})"
                    )
                )
                file_errors.append(image)

    if passed:
        print(term.green("All preflight checks passed! You're good to go."))
    else:
        print(term.red("Some preflight checks failed. You should fix them."))
    return passed


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    def handle(self, *args, **options):
        csvfile = options["csvfile"]
        f1 = open(csvfile)
        f2 = open(csvfile)

        logfile = f"{os.path.splitext(os.path.basename(csvfile))[0]}.log"
        logf_handle = open(logfile, "w")

        datareader = csv.DictReader(f1)
        print(term.green("Pre-checking spreadsheet for possible errors"))
        datareader_copy = csv.DictReader(f2)
        passed = preflight_checks(datareader_copy)

        if not passed:
            print(term.red("There were errors in the sources in this file."))
            cont = input("Type 'q' to quit or any key to continue: ")
            if cont == "q":
                sys.exit("Quitting.")

        for row in datareader:
            folder = row["folder"]
            source_id = row["source_id"]
            foldername = os.path.join("/data", "images", folder)
            source = Source.objects.get(pk=source_id)

            # get filenames in directory
            files = glob.glob(os.path.join(foldername, "*.jpx"))
            fns = [os.path.splitext(os.path.relpath(p, foldername))[0] for p in files]
            images = source.pages.values_list("images__pk", "images__legacy_filename")
            file_errors = []

            for image in images:
                if image[1] not in fns or re.match(r".*\s+.*", image[1]):
                    file_errors.append(image)

            print(
                term.yellow(
                    "\tFixing errors. 'k' will keep image entries, even if they're not found. 'r' will re-read the list of files"
                )
            )

            for err in file_errors:
                new_fn = _check_input(err[1], fns)
                img_to_fix = Image.objects.get(pk=err[0])

                if new_fn == "k":
                    logf_handle.write(
                        f"Image not found, but will be kept: {folder}/{err[1]}.jpx [Source {source.pk} ({source.display_name})]\n"
                    )
                    print(
                        term.yellow(
                            "\tKeeping the image in the database, but this *will* break things. Setting it to private to minimize the damage."
                        )
                    )
                    img_to_fix.public = False
                    img_to_fix.save()
                    continue

                if new_fn == "r":
                    print(term.yellow("\tRe-reading the list of files"))
                    rfiles = glob.glob(os.path.join(foldername, "*.jpx"))
                    rfns = [
                        os.path.splitext(os.path.relpath(p, foldername))[0]
                        for p in rfiles
                    ]
                    if err[1] not in rfns:
                        print(
                            term.red(
                                f"\tImage {err[1]} still not found in the list of filenames. Setting to private and continuing."
                            )
                        )
                        img_to_fix.public = False
                        img_to_fix.save()
                        continue

                img_to_fix.legacy_filename = new_fn
                img_to_fix.save()

            # re-fetch the pages + images after the errors have been fixed.
            pages = source.pages.all()
            for page in pages:
                for image in page.images.all():
                    location = f"https://{settings.HOSTNAME}/iiif/image/{folder}/{image.legacy_filename}.jpx"
                    print(
                        term.green(
                            f"\tSetting URL for image pk {image.pk} as {location}"
                        )
                    )
                    image.location = location
                    image.save()

                    url = urljoin(location + "/", "info.json")

                    r = requests.get(
                        url,
                        headers={
                            "referer": f"https://{settings.HOSTNAME}",
                            "X-DIAMM": settings.DIAMM_IMAGE_KEY,
                        },
                        timeout=10,
                    )

                    if 200 <= r.status_code < 300:
                        j = r.json()
                        image.iiif_response_cache = ujson.dumps(j)
                        image.save()
                    elif r.status_code == 404:
                        print(term.red(f"LOG: \t404 not found for {location}."))
                        logf_handle.write(
                            f"{folder}/{image.legacy_filename}.jpx was not found. [Source {source.pk} ({source.display_name})]\n"
                        )
                    else:
                        print(term.red(f"\tThere was a problem fetching {location}"))
                        print(term.red(f"\tThe error code was {r.status_code}"))
                        logf_handle.write(
                            f"Error code {r.status_code} when fetching {folder}/{image.legacy_filename}.jpx\n"
                        )

            print(term.blue(f"\tDone {source.display_name}"))
            print(term.blue("===========================================\n"))

        logf_handle.close()
        f1.close()
        f2.close()
