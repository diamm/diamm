from django.apps import AppConfig
import logging

# set up logging for SQL statements
# l = logging.getLogger('django.db.backends')
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())

class DiammDataAppConfig(AppConfig):
    name = 'diamm.diamm_data'
    verbose_name = 'DIAMM Data'
