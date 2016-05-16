import os

HOSTNAME = "alpha.diamm.ac.uk"

MEDIA_URL = "https://{0}/media/".format(HOSTNAME)
MEDIA_ROOT = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "diamm", "media"
)
STATIC_ROOT = "/srv/www/{0}/static".format(HOSTNAME)
LEGACY_IMAGE_DIR = "/Users/ahankins/Documents/code/git/diamm/testing/legacy"
IMAGE_DIR = '/Users/ahankins/Documents/code/git/diamm/testing/images'

