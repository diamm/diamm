from django.apps import AppConfig


# set up logging for SQL statements
# l = logging.getLogger('django.db.backends')
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())

class DiammSiteAppConfig(AppConfig):
    name = 'diamm.diamm_site'
    verbose_name = 'DIAMM Site'

    def ready(self):
        pass
