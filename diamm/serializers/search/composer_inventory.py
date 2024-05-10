import random

import serpy

from diamm.serializers.fields import StaticField
from diamm.serializers.serializers import ContextSerializer

"""
    An inventory by composer, where every 'composer' field is an array (possible
    multiple uncertain composers) is expensive to compute on the fly, so this will
    precompute all composer inventory relationships and store them in solr. This should
    allow us to also group on the composer pk and get all the compositions.

    type: composerinventory
    composer_i: $COMPOSER_PK
    composer_s: $COMPOSER_NAME
    source_i: $SOURCE_PK
    source_s: $SOURCE_NAME
    composition_s: $COMPOSITION_NAME
    composition_i: $COMPOSITION_PK
    uncertain_b: $UNCERTAINTY


('Alanus',
  'Johannes',
  8544,
  False,
  'Sub Arturo plebs valata / Fons citharizantium ac organizantium / In omnem terram',
  117,
  'Q.15',
  None,
  'I-Bc')
"""
# named indexes to keep things straight
LAST_NAME = 0
FIRST_NAME = 1
COMPOSER_PK = 2
UNCERTAIN = 3
COMPOSITION_TITLE = 4
SOURCE_ID = 5
SOURCE_SHELFMARK = 6
SOURCE_NAME = 7
ARCHIVE_SIGLUM = 8
COMPOSITION_PK = 9
FOLIO_START = 10
FOLIO_END = 11
SOURCE_ATTRIBUTION = 12
ITEM_PK = 13

# These fields will be used in two places, so they are stored centrally here and then
# imported in the reindexing signal and in the reindex_all script.
FIELDS_TO_INDEX = [
    'composition__composers__composer__last_name',
    'composition__composers__composer__first_name',
    'composition__composers__composer__pk',
    'composition__composers__uncertain',
    'composition__title',
    'source_id',
    'source__shelfmark',
    'source__name',
    'source__archive__siglum',
    'composition__pk',
    'folio_start',
    'folio_end',
    'source_attribution',
    'pk'  # item pk
]


class ComposerInventorySearchSerializer(ContextSerializer):
    type = StaticField(
        value="composerinventory"
    )
    pk = serpy.MethodField()
    composer_s = serpy.MethodField()
    composer_i = serpy.MethodField()
    source_i = serpy.MethodField()
    uncertain_b = serpy.MethodField()
    composition_s = serpy.MethodField()
    composition_i = serpy.MethodField()
    folio_start_s = serpy.MethodField()
    folio_end_s = serpy.MethodField()
    source_attribution_s = serpy.MethodField()
    item_i = serpy.MethodField()

    # The PK for this table does not map directly on to any
    # database entity, so we can instead generate a random integer
    # and use that.
    def get_pk(self, obj):
        return random.randrange(10000000)

    def get_composer_s(self, obj):
        if obj[LAST_NAME] and obj[FIRST_NAME]:
            return f"{obj[LAST_NAME]}, {obj[FIRST_NAME]}"
        elif obj[LAST_NAME]:
            return f"{obj[LAST_NAME]}"

        return "Anonymous"

    def get_composer_i(self, obj):
        if obj[COMPOSER_PK]:
            return obj[COMPOSER_PK]
        return None

    def get_source_i(self, obj):
        return obj[SOURCE_ID]

    def get_uncertain_b(self, obj):
        return obj[UNCERTAIN] is True

    def get_composition_s(self, obj):
        return obj[COMPOSITION_TITLE]

    def get_composition_i(self, obj):
        return obj[COMPOSITION_PK]

    def get_folio_start_s(self, obj):
        return obj[FOLIO_START]

    def get_folio_end_s(self, obj):
        return obj[FOLIO_END]

    def get_source_attribution_s(self, obj):
        return obj[SOURCE_ATTRIBUTION]

    def get_item_i(self, obj):
        return obj[ITEM_PK]
