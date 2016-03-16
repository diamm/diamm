from urllib.parse import urljoin
import requests
import ujson
from django.core.management import BaseCommand
from diamm.models.data.image import Image

IIP_SERVER_BASE = "http://www.diamm.ac.uk/iiif/image/"


def _image_data_request(location):
    # ensure a trailing slash so urljoin doesn't remove the identifier.
    url = urljoin(location + "/", "info.json")
    r = requests.get(url, headers={'referer': 'http://alpha.diamm.ac.uk'})
    if r.status_code == 200:
        return r.json()
    else:
        # mock the image data with 0x0 for any errors.
        print('Error parsing request for {0}: status code was {1}'.format(url, r.status_code))
        return None


class Command(BaseCommand):
    def handle(self, *args, **options):
        imgurls = open('imageurls.txt', 'w')
        imgs = Image.objects.filter(public=True).only('legacy_filename', 'location')
        for img in imgs:
            # all filenames are .jp2
            fn = "{0}.jp2".format(img.legacy_filename)

            location = urljoin(IIP_SERVER_BASE, fn)
            print("{0} ===> {1}".format(fn, location))
            img.location = location
            # img_data = _image_data_request(location)
            # if img_data:
            #     img.iiif_response_cache = ujson.dumps(img_data)
            # else:
            #     img.iiif_response_cache = None
            img.save()
            imgurls.write(location + "\n")

        imgurls.close()



