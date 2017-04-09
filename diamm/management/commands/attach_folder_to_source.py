from django.core.management.base import BaseCommand
from django.conf import settings
import argparse
import csv
import os
import glob
import sys
from diamm.models.data.source import Source
from diamm.models.data.image import Image
import blessings
import re
import requests
from urllib.parse import urljoin
import ujson

term = blessings.Terminal()


def _check_input(imagename, filenames):
    while True:
        possible_default = re.sub(r'Add\.', 'Add', imagename)
        inp = input("Fix {0} ([{1}]?): ".format(imagename, possible_default))

        # Accept the default. This will still get checked against the list of available filenames.
        if not inp:
            inp = possible_default

        # Allow the user to choose to delete or keep this image without matching a filename. Use with caution.
        if inp in ('d', 'k'):
            return inp

        if inp not in filenames:
            print(term.red("{0} is not in the list of filenames. Please try again.".format(inp)))
            continue
        else:
            break

    return inp


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        csvfile = options['csvfile']

        logfile = "{0}.log".format(os.path.splitext(os.path.basename(csvfile.name))[0])
        logf_handle = open(logfile, 'w')

        datareader = csv.DictReader(csvfile)
        print(term.green('Pre-checking spreadsheet for possible errors'))

        for row in datareader:
            # sanity checking
            folder = row['folder']
            source = row['source_id']
            print(term.blue("Checking {0}...".format(folder)))
            # check that the folder exists
            foldername = os.path.join("/data", "images", folder)
            if not os.path.exists(foldername):
                sys.exit("folder name {0} does not exist. Please check this entry and re-try.".format(folder))

            # check that the source exists
            try:
                source = Source.objects.get(pk=source)
            except Source.DoesNotExist:
                sys.exit("source {0} does not exist. Please check this entry and re-try".format(source))
            print(term.cyan("Found source {0}\n".format(term.white(source.display_name))))
            logf_handle.write("=== {0} ===\n".format(source.display_name))

            # get filenames in directory
            files = glob.glob(os.path.join(foldername, "*.jpx"))
            fns = [os.path.splitext(os.path.relpath(p, foldername))[0] for p in files]
            images = source.pages.values_list('images__pk', 'images__legacy_filename')
            file_errors = []

            for image in images:
                if image[1] not in fns:
                    print(term.red("NOT_FOUND:\tImage {t.white}{0}{t.red} (pk {1}) in the database is not in the list of available files.".format(image[1], image[0], t=term)))
                    file_errors.append(image)

                if re.match(r'.*\s+.*', image[1]):
                    print(term.red("SPACES_IN_NAME:\tThere were spaces in Image {t.white}{0}{t.red} (pk {1})".format(image[1], image[0], t=term)))
                    file_errors.append(image)

            if file_errors:
                print(term.red('\nThere were errors. Before any database changes are made, would you like to exit and fix them?'))
                cont = input("Type 'q' to quit or any key to continue: ")
                if cont == "q":
                    sys.exit("Quitting.")

                print(term.yellow("\tFixing errors. 'k' will keep image entries, even if they're not found."))

                for err in file_errors:
                    new_fn = _check_input(err[1], fns)
                    img_to_fix = Image.objects.get(pk=err[0])

                    if new_fn == 'k':
                        logf_handle.write("Image not found, but will be kept: {0}/{1}.jpx [Source {2} ({3})]\n".format(folder, err[1], source.pk, source.display_name))
                        print(term.yellow("\tKeeping the image in the database, but this *will* break things. Setting it to private to minimize the damage."))
                        img_to_fix.public = False
                        img_to_fix.save()
                        continue

                    img_to_fix.legacy_filename = new_fn
                    img_to_fix.save()

            # re-fetch the pages + images after the errors have been fixed.
            pages = source.pages.all()
            for page in pages:
                for image in page.images.all():
                    location = "https://{0}/iiif/image/{1}/{2}.jpx".format(settings.HOSTNAME, folder, image.legacy_filename)
                    print(term.green("\tSetting URL for image pk {0} as {1}".format(image.pk, location)))
                    image.location = location
                    image.save()

                    url = urljoin(location + "/", "info.json")

                    r = requests.get(url, headers={
                        "referer": "https://{0}".format(settings.HOSTNAME),
                        "X-DIAMM": settings.DIAMM_IMAGE_KEY
                    })

                    if 200 <= r.status_code < 300:
                        j = r.json()
                        image.iiif_response_cache = ujson.dumps(j)
                        image.save()
                    elif r.status_code == 404:
                        print(term.red("LOG: \t404 not found for {0}.".format(location)))
                        logf_handle.write("{0}/{1}.jpx was not found. [Source {2} ({3})]\n".format(folder, image.legacy_filename, source.pk, source.display_name))
                    else:
                        print(term.red("\tThere was a problem fetching {0}".format(location)))
                        print(term.red("\tThe error code was {0}".format(r.status_code)))
                        logf_handle.write("Error code {0} when fetching {1}/{2}.jpx\n".format(r.status_code, folder, image.legacy_filename))

            print(term.blue("\tDone {0}".format(source.display_name)))
            print(term.blue("===========================================\n"))

        logf_handle.close()
