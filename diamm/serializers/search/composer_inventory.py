import logging

import ypres

from diamm.serializers.search.helpers import (
    get_db_records,
    parallelise,
    process_composers,
    record_indexer,
)

log = logging.getLogger("diamm")


def index_composer_inventory(cfg: dict) -> bool:
    log.info("Indexing composer inventory")
    record_groups = _get_inventory(cfg)
    parallelise(
        record_groups, record_indexer, create_composer_inventory_index_documents, cfg
    )

    return True


def _get_inventory(cfg: dict):
    sql_query = """SELECT p.id AS person_id, floor(random() * 100000000 + 1)::int AS pk,
                        'composerinventory' AS record_type, array_agg(it.id) AS items, it.source_id AS source_id,
                       jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                                 'id', it.composition_id,
                                 'title', c.title,
                                 'folio_start', it.folio_start,
                                 'folio_end', it.folio_end,
                                 'attribution', it.source_attribution,
                                 'uncertain', cc.uncertain,
                                 'fragment', it.fragment,
                                 'completeness', it.completeness,
                                 'source_id', it.source_id,
                                 'page_id', first_page.page_id,
                                 'page_external', first_page.external,
                                 'page_canvas_uri', first_page.iiif_canvas_uri
                                 )) ORDER BY c.title) AS compositions,
                       jsonb_agg(DISTINCT jsonb_strip_nulls(jsonb_build_object(
                                        'id', p.id,
                                        'last_name', p.last_name,
                                        'first_name', p.first_name,
                                        'earliest_year', p.earliest_year,
                                        'latest_year', p.latest_year,
                                        'earliest_year_approximate', p.earliest_year_approximate,
                                        'latest_year_approximate', p.latest_year_approximate,
                                        'floruit', p.floruit
                                         ))) AS composer
                FROM diamm_data_item AS it
                LEFT JOIN diamm_data_compositioncomposer AS cc ON cc.composition_id = it.composition_id
                LEFT JOIN diamm_data_person AS p ON cc.composer_id = p.id
                LEFT JOIN diamm_data_composition AS c ON it.composition_id = c.id
                LEFT JOIN LATERAL (
                    SELECT page.id AS page_id,
                           page.external AS external,
                           page.iiif_canvas_uri AS iiif_canvas_uri
                      FROM diamm_data_item_pages AS item_page
                      JOIN diamm_data_page AS page ON page.id = item_page.page_id
                     WHERE item_page.item_id = it.id
                     ORDER BY page.sort_order ASC NULLS LAST, page.id ASC
                     LIMIT 1
                ) AS first_page ON TRUE
                GROUP BY it.source_id, p.id"""

    return get_db_records(sql_query, cfg)


def create_composer_inventory_index_documents(record, cfg: dict):
    return [ComposerInventorySearchSerializer(record).serialized]


class ComposerInventorySearchSerializer(ypres.DictSerializer):
    type = ypres.StrField(attr="record_type")
    pk = ypres.IntField()
    composer_s = ypres.MethodField()
    composer_i = ypres.IntField(attr="person_id", required=False)
    source_i = ypres.IntField(attr="source_id", required=False)
    compositions_json = ypres.MethodField()
    items_ii = ypres.Field(attr="items", required=False)

    def get_composer_s(self, obj) -> str | None:
        if obj.get("person_id") is None:
            return "Anonymous"
        composers = process_composers(obj["composer"], None)
        ret = [c[0] for c in composers]
        if ret:
            return ret[0]
        return None

    def get_compositions_json(self, obj) -> list[str]:
        return obj["compositions"]
