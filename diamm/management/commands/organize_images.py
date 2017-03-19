import os
import re
import shutil
import unicodedata
from django.conf import settings
from django.db.models import signals
from django.core.management import BaseCommand
from diamm.models.data.image import Image
from diamm.signals.page_signals import index_image
from diamm.models.data.source import Source

STORE0 = "/dbdata2"
STORE1 = "/dbdata4"
OLDPATH = "/dbdata3/diamm/images"
HOSTNAME = "beta.diamm.ac.uk"

TEST = False

RE_spaces = r"[\s]+"
RE_remove = r'[:,\.\[\](){}"\'\*/]+'
RE_underscores = r"[_]+"


def list_duplicates(l):
    seen = set()
    seen_add = seen.add
    seen_twice = set( x for x in l if x in seen or seen_add(x))
    return list(seen_twice)


class Command(BaseCommand):
    def _foldername(self, source):
        sn = re.sub(RE_remove, "", source.shelfmark)
        sn = re.sub(RE_spaces, "_", sn)

        sg = re.sub(RE_remove, "", source.archive.siglum)
        sg = re.sub(RE_spaces, "_", sg)
        n = "{0}_{1}_{2}".format(sg, sn, source.pk)
        n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode('ascii')
        return n

    def handle(self, *args, **options):
        signals.post_save.disconnect(index_image, sender=Image)
        log = open('missing_images.txt', 'w')

        sources = Source.objects.all().select_related('archive').order_by('pk')

        # pre-check duplicates
        fnames = []
        for source in sources:
            if source.pages.count() == 0:
                continue

            # split the image storage over two drives based on even/odd source pks so we don't fill it up.
            store = None
            urlpath = None
            if source.pk % 2 == 0:
                store = STORE0
                urlpath = "https://{0}/iiif/image/store0/".format(HOSTNAME)
            else:
                store = STORE1
                urlpath = "https://{0}/iiif/image/store1/".format(HOSTNAME)

            foldername = self._foldername(source)
            pathname = os.path.join(store, foldername)

            # if os.path.exists(pathname):
            #     print('path exists. Bailing')
            #     sys.exit(-1)

            if not TEST:
                try:
                    os.mkdir(pathname)
                except FileExistsError:
                    pass

            for page in source.pages.all():
                pname = page.numeration
                # print("\t{0}".format(pname))
                for image in page.images.all():
                    if not image.legacy_filename:
                        continue

                    imgurl = "{0}{1}/{2}.jp2".format(urlpath, foldername, image.legacy_filename)

                    # print("\t{0}.jp2 ===> {1}".format(os.path.join(pathname, image.legacy_filename), imgurl))

                    if not TEST:
                        try:
                            shutil.move(os.path.join(OLDPATH, "{0}.jp2".format(image.legacy_filename)), pathname)
                            image.location = imgurl
                            image.save()
                        except FileNotFoundError:
                            if source.public_images:
                                log.write("{0}\t{1}\n".format(source.pk, image.legacy_filename))
                            pass
