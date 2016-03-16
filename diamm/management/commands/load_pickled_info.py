from django.core.management import BaseCommand
from diamm.models.data.page import Page
from diamm.models.data.image import Image
import pickle
import ujson
import sys


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('urloutput.pickle', 'rb') as f:
            data = pickle.load(f)
            for k, v in data.items():
                print(k)
                try:
                    image = Image.objects.get(location=k)
                except Image.MultipleObjectsReturned:
                    image = Image.objects.filter(location=k).first()

                if not image:
                    print("OH NO NO IMAGE FOUND!")
                    sys.exit(-1)

                image.iiif_response_cache = ujson.dumps(v)
                image.save()
