import logging
from pathlib import Path

import blessings
from django.conf import settings
from django.core.management.base import BaseCommand

from diamm.models.data.image import Image

term = blessings.Terminal()
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        images = Image.objects.all()

        for im in images:
            image_exists = Path(settings.IMAGE_DIR, im.location).exists()
            if not image_exists:
                log.error(f"Image {im.id} with path of {im.location} does not exist.")
