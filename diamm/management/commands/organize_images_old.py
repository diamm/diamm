import re
import os
import shutil
import sys
import unicodedata
from django.core.management import BaseCommand
import hashlib
from django.conf import settings
from diamm.models.data.image import Image
from diamm.models.data.source import Source
from blessings import Terminal

term = Terminal()

RE_spaces = r"[\s()\[\]:/]+"
RE_remove = r'[,(){}"\'\*]+'
RE_underscores = r"[_]+"


def clean_dirname(msdir):
    # remove any extraneous spaces
    newdir = msdir.replace("/", " ")
    newdir = re.sub(RE_remove, "", newdir)
    newdir = re.sub(RE_spaces, "_", newdir)
    # ensure we only ever have one underscore (in case there was " _")
    newdir = re.sub(RE_underscores, "_", newdir)
    newdir = unicodedata.normalize('NFKD', newdir).encode('ascii', 'ignore')

    return str(newdir, 'ascii')


class Command(BaseCommand):
    def handle(self, *args, **options):
        images = Image.objects.all().prefetch_related('items__source__archive')

        for img in images:
            if img.filename in (None, 'applytolibrary', 'not photographed', 'librarydigitized'):
                continue

            items = img.items.all()
            for it in items:
                potential_foldername = "{0}_{1}".format(it.source.archive.siglum, it.source.shelfmark)
                foldername = clean_dirname(potential_foldername)
                new_path = os.path.join(settings.IMAGE_DIR, foldername)
                if not os.path.exists(new_path):
                    print(term.blue("Making {0}".format(foldername)))
                    os.mkdir(new_path)

                imgfn = "{0}.jp2".format(img.filename)
                legacy_img = os.path.join(settings.LEGACY_IMAGE_DIR, imgfn)

                print(term.green("Moving {0} to {1}".format(legacy_img, os.path.join(new_path, imgfn))))
                try:
                    os.rename(legacy_img, os.path.join(new_path, imgfn))
                    # copy for testing
                    # shutil.copy(legacy_img, new_path)
                except FileNotFoundError as e:
                    print(term.red("\tSkipping {0} (moved previously?)".format(legacy_img)))

