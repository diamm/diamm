import functools
import logging

import ypres
import ujson

from diamm.serializers.search.helpers import (
    get_db_records,
    parallelise,
    record_indexer,
    process_bibliography_entries,
)

log = logging.getLogger("diamm")


def index_bibliography(cfg: dict) -> bool:
    log.info("Indexing bibliography")
    record_groups = _get_bibliography(cfg)
    parallelise(record_groups, record_indexer, create_bibliography_index_documents, cfg)

    return True


def _get_bibliography(cfg: dict):
    sql_query = """SELECT b.id AS pk, 'bibliography' AS record_type, b.title AS title, b.year AS year,
                   b.abbreviation AS abbreviation,
                   (SELECT t.name
                        FROM diamm_data_bibliographytype AS t
                        WHERE b.type_id = t.id
                   ) AS type_name,
                   (SELECT (jsonb_agg(jsonb_build_object(
                                    'position', bar.position,
                                    'last_name', ba.last_name,
                                    'id', ba.id
                                    ) ORDER BY bar.position, ba.last_name))
                        FROM diamm_data_bibliographyauthorrole AS bar
                        LEFT JOIN diamm_data_bibliographyauthor ba on bar.bibliography_author_id = ba.id
                        WHERE bar.bibliography_entry_id = b.id
                   ) AS authors,
                   (SELECT jsonb_build_object(
                       'title', bib.title,
                       'type', bib.type_id,
                       'year', bib.year,
                       'people', (SELECT jsonb_agg(jsonb_build_object(
                                               'id', bau1.id,
                                               'last_name', bau1.last_name,
                                               'first_name', bau1.first_name,
                                               'role', bar1.role,
                                               'position', bar1.position
                                       ))
                                       FROM diamm_data_bibliographyauthorrole AS bar1
                                       LEFT JOIN diamm_data_bibliographyauthor AS bau1 ON bar1.bibliography_author_id = bau1.id
                                       WHERE bib.id = bar1.bibliography_entry_id),
                       'publication', (SELECT jsonb_agg(jsonb_build_object(
                                                'id', bpu1.id,
                                                'type', bpu1.type,
                                                'entry', bpu1.entry
                                        ))
                                        FROM diamm_data_bibliographypublication AS bpu1
                                        WHERE bpu1.bibliography_id = bib.id)
                       ) FROM diamm_data_bibliography AS bib
                       WHERE b.id = bib.id
                       GROUP BY bib.id
                   ) AS publication_info,
                   (SELECT jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                        'source_id', s.source_id,
                        'primary_study', s.primary_study,
                        'pages', s.pages,
                        'notes', s.notes
                        )))
                        FROM diamm_data_sourcebibliography AS s
                        WHERE s.bibliography_id = b.id
                   ) AS sources,
                   (SELECT jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                        'set_id', s.set_id,
                        'pages', s.pages,
                        'notes', s.notes
                        )))
                        FROM diamm_data_setbibliography AS s
                        WHERE s.bibliography_id = b.id
                   ) AS sets,
                   (SELECT jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                            'item_id', i.item_id,
                            'pages', i.pages,
                            'notes', i.notes
                        )))
                        FROM diamm_data_itembibliography AS i
                        WHERE i.bibliography_id = b.id
                   ) AS items,
                   (SELECT jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                            'composition_id', c.composition_id,
                            'pages', c.pages,
                            'notes', c.notes
                        )))
                        FROM diamm_data_compositionbibliography AS c
                        WHERE c.bibliography_id = b.id
                   ) AS compositions
            FROM diamm_data_bibliography AS b
            ORDER BY b.id;"""

    return get_db_records(sql_query, cfg)


def create_bibliography_index_documents(record, cfg: dict):
    return [BibliographySearchSerializer(record).serialized]


class BibliographySearchSerializer(ypres.DictSerializer):
    type = ypres.StrField(attr="record_type")
    pk = ypres.IntField()

    authors_ss = ypres.MethodField()
    authors_ii = ypres.MethodField()

    title_s = ypres.StrField(attr="title")
    year_s = ypres.StrField(attr="year")
    year_ans = ypres.StrField(attr="year")
    type_s = ypres.StrField(attr="type_name")
    abbreviation_s = ypres.StrField(attr="abbreviation")
    citation_json = ypres.MethodField()
    sort_ans = ypres.MethodField()
    sources_ii = ypres.MethodField()
    sets_ii = ypres.MethodField()
    sources_json = ypres.MethodField()
    sets_json = ypres.MethodField()
    items_ii = ypres.MethodField()
    items_json = ypres.MethodField()
    compositions_ii = ypres.MethodField()
    compositions_json = ypres.MethodField()

    def get_authors_ss(self, obj):
        """
        Construct a sortable author list representation, with authors separated by $:
        Position|Last Name|PK$Position|Last Name|PK$...

        This should allow authors to sort first by position, then by last name, and use their
        PK for reverse URL lookups on the other end.
        """
        authors = process_authors(obj["authors"])
        return [f"{n[0]}|{n[1]}|{n[2]}" for n in authors] if authors else None

    def get_authors_ii(self, obj):
        authors = process_authors(obj["authors"])
        return [n[2] for n in authors] if authors else None

    def get_sort_ans(self, obj) -> str | None:
        authors = process_authors(obj["authors"]) or []
        last_names = [n[1] for n in authors]
        return " ".join(last_names) if authors else None

    def get_sources_ii(self, obj):
        if not obj.get("sources"):
            return None
        sources = process_sources(obj["sources"])
        return [s["source_id"] for s in sources]

    def get_sets_ii(self, obj):
        if not obj.get("sets"):
            return None
        sets = process_sets(obj["sets"])
        return [s["set_id"] for s in sets]

    def get_sources_json(self, obj):
        if not obj.get("sources"):
            return None
        return obj["sources"]

    def get_sets_json(self, obj):
        if not obj.get("sets"):
            return None
        return obj["sets"]

    def get_items_ii(self, obj):
        if not obj.get("items"):
            return None
        items = process_items(obj["items"])
        return [i["item_id"] for i in items]

    def get_items_json(self, obj):
        if not obj.get("items"):
            return None
        return obj["items"]

    def get_compositions_ii(self, obj):
        if not obj.get("compositions"):
            return None
        compositions = process_items(obj["compositions"])
        return [c["composition_id"] for c in compositions]

    def get_compositions_json(self, obj):
        if not obj.get("compositions"):
            return None
        return obj["compositions"]

    def get_citation_json(self, obj):
        """
        Pre-renders the citation by passing it through the Jinja template
        engine. This is an optimization to help reduce the amount of time
        needed to render the citation on request.
        """
        entries: dict = ujson.loads(obj["publication_info"])
        return ujson.dumps(process_bibliography_entries(entries))
        # template = get_template("website/bibliography/bibliography_entry.jinja2")
        # citation = template.template.render(content=obj)
        # # strip out any newlines from the templating process
        # citation = re.sub(r"\n", "", citation)
        # # strip out multiple spaces
        # citation = re.sub(r"\s+", " ", citation)
        # citation = citation.strip()
        # return citation


@functools.lru_cache
def process_sources(sources_str: str | None):
    return ujson.loads(sources_str) if sources_str else []


@functools.lru_cache
def process_sets(sets_str: str | None):
    return ujson.loads(sets_str) if sets_str else []


@functools.lru_cache
def process_items(items_str: str | None):
    return ujson.loads(items_str) if items_str else []


@functools.lru_cache
def process_compositions(compositions_str: str | None):
    return ujson.loads(compositions_str) if compositions_str else []


@functools.lru_cache
def process_authors(author_str: str | None) -> list | None:
    authors = ujson.loads(author_str) if author_str else []
    return [(a["position"], a["last_name"], a["id"]) for a in authors]
