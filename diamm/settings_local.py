import os

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "diamm", "media"
)
STATIC_ROOT = "/srv/www/alpha.diamm.ac.uk/static"
LEGACY_IMAGE_DIR = "/Users/ahankins/Documents/code/git/diamm/testing/legacy"
IMAGE_DIR = '/Users/ahankins/Documents/code/git/diamm/testing/images'

