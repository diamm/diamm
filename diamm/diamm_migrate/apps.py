from django.apps import AppConfig
import logging

# set up logging for SQL statements
# l = logging.getLogger('django.db.backends')
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())

class DiammMigrateAppConfig(AppConfig):
    name = 'diamm.diamm_migrate'
    verbose_name = 'DIAMM Migrate'
