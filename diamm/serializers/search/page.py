import logging

import serpy

from diamm.serializers.search.helpers import (
    get_db_records,
    parallelise,
    record_indexer,
)

log = logging.getLogger("diamm")


def index_pages_and_images(cfg: dict) -> bool:
    log.info("Indexing pages")
    page_records = _get_pages(cfg)
    parallelise(page_records, record_indexer, create_page_index_documents, cfg)

    log.info("Indexing images")
    image_records = _get_images(cfg)
    parallelise(image_records, record_indexer, create_image_index_documents, cfg)

    return True


def _get_pages(cfg):
    sql_query = """SELECT p.id AS pk, 'page' AS record_type, p.page_type AS page_type,
                          COALESCE(((json_build_object(
                                   1, 'Page',
                                   2, 'Modern Endpapers',
                                   3, 'Contemporary Endpapers',
                                   4, 'Flyleaf',
                                   5, 'Opening',
                                   6, 'Bindings',
                                   7, 'Fragment(s)',
                                   8, 'Scroll',
                                   9, 'Additional',
                                   10, 'Pastedown',
                                   11, 'Offset',
                                   12, 'Secondary'
                            )::jsonb)->>(page_type::integer)::text
                           )::text, ''
                          ) AS page_kind, p.numeration AS numeration, p.sort_order AS sort_order,
                          p.source_id AS source_id, p.external AS external, p.iiif_canvas_uri AS iiif_canvas_uri,
                          (SELECT array_agg(i.id)
                             FROM diamm_data_item_pages AS i
                            WHERE i.page_id = p.id)
                          AS items,
                          (SELECT array_agg(im.location)
                             FROM diamm_data_image AS im
                            WHERE im.public IS TRUE AND im.page_id = p.id
                                  AND im.width != 0 AND im.height != 0)
                          AS images
                     FROM diamm_data_page AS p
                 ORDER BY p.id"""

    return get_db_records(sql_query, cfg)


def _get_images(cfg):
    sql_query = """SELECT i.id AS pk, 'image' AS record_type, i.location AS location,
                          i.type_id AS type_id, i.width AS width, i.height AS height,
                          i.external AS external, i.page_id AS page_id, p.numeration AS numeration,
                          p.sort_order AS sort_order, p.source_id AS source_id,
                          (SELECT it.name
                             FROM diamm_data_imagetype AS it
                            WHERE i.type_id = it.id) AS image_type,
                          (SELECT array_agg(i2.id)
                             FROM diamm_data_image AS i2
                             WHERE i2.page_id = p.id AND i2.public IS TRUE
                                    AND i2.type_id != 1 AND i2.width != 0
                                    AND i2.height != 0)
                          AS alt_images
                     FROM diamm_data_image AS i
                     LEFT JOIN diamm_data_page AS p ON i.page_id = p.id
                    WHERE i.public IS TRUE AND i.page_id IS NOT NULL
                          AND i.width != 0 AND i.height != 0
                 ORDER BY i.id"""
    return get_db_records(sql_query, cfg)


def create_page_index_documents(record, cfg):
    return [PageSearchSerializer(record).data]


def create_image_index_documents(record, cfg):
    return [ImageSearchSerializer(record).data]


class ImageSearchSerializer(serpy.DictSerializer):
    type = serpy.StrField(attr="record_type")
    pk = serpy.IntField()
    page_i = serpy.IntField(attr="page_id")

    source_i = serpy.IntField(attr="source_id")
    location_s = serpy.StrField(attr="location", required=False)
    image_type_i = serpy.IntField(attr="type_id", required=False)
    image_type_s = serpy.StrField(attr="image_type", required=False)
    numeration_s = serpy.StrField(attr="numeration", required=False)
    numeration_ans = serpy.StrField(attr="numeration", required=False)
    sort_order_f = serpy.FloatField(attr="sort_order", required=False)
    alt_images_ii = serpy.Field(attr="alt_images", required=False)

    width_i = serpy.IntField(attr="width")
    height_i = serpy.IntField(attr="height")
    external_b = serpy.BoolField(attr="external")


class PageSearchSerializer(serpy.DictSerializer):
    type = serpy.StrField(attr="record_type")
    pk = serpy.IntField()
    page_type_i = serpy.IntField(attr="page_type", required=False)
    page_type_s = serpy.StrField(attr="page_kind", required=False)

    numeration_s = serpy.StrField(attr="numeration")
    numeration_ans = serpy.StrField(attr="numeration")
    sort_order_f = serpy.FloatField(attr="sort_order")
    source_i = serpy.IntField(attr="source_id")
    items_ii = serpy.Field(attr="items")
    images_ss = serpy.Field(attr="images")
    iiif_canvas_uri_s = serpy.StrField(attr="iiif_canvas_uri")
    external_b = serpy.BoolField(attr="external")
