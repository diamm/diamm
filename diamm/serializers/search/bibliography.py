import functools
import logging

import serpy
import ujson

from diamm.serializers.search.helpers import get_db_records, parallelise, record_indexer

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
                    WHERE b.type_id = t.id) AS type_name,
                   (SELECT (jsonb_agg(jsonb_build_object(
                                    'position', bar.position,
                                    'last_name', ba.last_name,
                                    'id', ba.id
                                    ) ORDER BY bar.position, ba.last_name))
                        FROM diamm_data_bibliographyauthorrole AS bar
                        LEFT JOIN diamm_data_bibliographyauthor ba on bar.bibliography_author_id = ba.id
                        WHERE bar.bibliography_entry_id = b.id)
                    AS authors,
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
                 GROUP BY bib.id)
                AS publication_info,
                (SELECT jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                        'source_id', s.source_id,
                        'primary_study', s.primary_study,
                        'pages', s.pages,
                        'notes', s.notes
                    )))
                    FROM diamm_data_sourcebibliography AS s
                    WHERE s.bibliography_id = b.id)
                AS sources,
                (SELECT jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                    'set_id', s.set_id,
                    'pages', s.pages,
                    'notes', s.notes
                    )))
                    FROM diamm_data_setbibliography AS s
                    WHERE s.bibliography_id = b.id)
                AS sets,
                (SELECT jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                        'item_id', i.item_id,
                        'pages', i.pages,
                        'notes', i.notes
                    )))
                    FROM diamm_data_itembibliography AS i
                    WHERE i.bibliography_id = b.id)
                AS items,
                (SELECT jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
                        'composition_id', c.composition_id,
                        'pages', c.pages,
                        'notes', c.notes
                    )))
                    FROM diamm_data_compositionbibliography AS c
                    WHERE c.bibliography_id = b.id)
                AS compositions
            FROM diamm_data_bibliography AS b
            ORDER BY b.id;"""

    return get_db_records(sql_query, cfg)


def create_bibliography_index_documents(record, cfg: dict):
    return [BibliographySearchSerializer(record).data]


class BibliographySearchSerializer(serpy.DictSerializer):
    type = serpy.StrField(attr="record_type")
    pk = serpy.IntField()

    authors_ss = serpy.MethodField()
    authors_ii = serpy.MethodField()

    title_s = serpy.StrField(attr="title")
    year_s = serpy.StrField(attr="year")
    year_ans = serpy.StrField(attr="year")
    type_s = serpy.StrField(attr="type_name")
    abbreviation_s = serpy.StrField(attr="abbreviation")
    citation_json = serpy.MethodField()
    sort_ans = serpy.MethodField()
    sources_ii = serpy.MethodField()
    sets_ii = serpy.MethodField()
    sources_json = serpy.MethodField()
    sets_json = serpy.MethodField()
    items_ii = serpy.MethodField()
    items_json = serpy.MethodField()
    compositions_ii = serpy.MethodField()
    compositions_json = serpy.MethodField()

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
        authors = process_authors(obj["authors"])
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
        return ujson.dumps(process_bibliography_entries(obj["publication_info"]))
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


def process_bibliography_entries(bibliography_str: str | None):
    if not bibliography_str:
        return None
    entries = ujson.loads(bibliography_str)

    authors = []
    editors = []
    compilers = []
    if ep := entries["people"]:
        for entry in ep:
            match entry["role"]:
                case 1:
                    authors.append(entry)
                case 2:
                    editors.append(entry)
                case 3:
                    compilers.append(entry)

    volume_nos = []
    parent_titles = []
    publishers = []
    pages = []
    university = []
    degree = []
    chapter = []
    series = []
    url = []
    url_accessed = []
    translator = []
    festschrift_for = []
    place_publication = []
    num_volumes = []
    intl_num = []
    conference_name = []
    conference_location = []
    conference_date = []
    note = []

    if epub := entries["publication"]:
        for entry in epub:
            match entry["type"]:
                case 1:
                    volume_nos.append(entry)
                case 2:
                    parent_titles.append(entry)
                case 3:
                    publishers.append(entry)
                case 4:
                    pages.append(entry)
                case 5:
                    university.append(entry)
                case 6:
                    degree.append(entry)
                case 7:
                    chapter.append(entry)
                case 8:
                    series.append(entry)
                case 9:
                    url.append(entry)
                case 10:
                    url_accessed.append(entry)
                case 11:
                    translator.append(entry)
                case 12:
                    festschrift_for.append(entry)
                case 13:
                    place_publication.append(entry)
                case 14:
                    num_volumes.append(entry)
                case 15:
                    intl_num.append(entry)
                case 16:
                    conference_name.append(entry)
                case 17:
                    conference_location.append(entry)
                case 18:
                    conference_date.append(entry)
                case 99:
                    note.append(entry)

    return {
        "title": entries["title"],
        "type": entries["type"],
        "year": entries["year"],
        "authors": authors,
        "editors": editors,
        "compilers": compilers,
        "volumes": volume_nos,
        "parent_titles": parent_titles,
        "publishers": publishers,
        "pages": pages,
        "university": university,
        "degree": degree,
        "chapter": chapter,
        "series": series,
        "url": url,
        "url_accessed": url_accessed,
        "translator": translator,
        "festschrift_for": festschrift_for,
        "place_publication": place_publication,
        "num_volumes": num_volumes,
        "intl_num": intl_num,
        "conference_name": conference_name,
        "conference_location": conference_location,
        "conference_date": conference_date,
        "note": note,
    }
