import concurrent.futures
import functools
import logging
from collections.abc import Callable, Iterable
from operator import itemgetter
from typing import Optional

import httpx
import ujson
from django.db import connection

log = logging.getLogger("diamm")


def get_db_records(sql_query: str, cfg: dict):
    with connection.cursor() as cursor:
        cursor.execute(sql_query)

        columns = [col[0] for col in cursor.description]

        while rows := cursor.fetchmany(size=cfg["resultsize"]):
            yield [dict(zip(columns, row)) for row in rows]


def parallelise(records: Iterable, func: Callable, *args, **kwargs) -> None:
    """
    Given a list of records, this function will parallelise processing of those records. It will
    coalesce the arguments into an array, to be handled by function `func`.

    :param records: A list of records to be processed by `func`. Should be the first argument
    :param func: A function to process and index the records
    :param func: A shared Solr connection object
    :return: None
    """
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures_list = [
            executor.submit(func, record, *args, **kwargs) for record in records
        ]

        for f in concurrent.futures.as_completed(futures_list):
            f.result()


def record_indexer(records: list, converter: Callable, cfg: dict) -> bool:
    idx_records = []
    log.info("processing record group with", converter.__name__)
    for record in records:
        docs: list = converter(record, cfg)
        idx_records.extend(docs)

    check: bool = True if cfg["dry"] else submit_to_solr(idx_records, cfg)

    if not check:
        log.error("There was an error indexing records.")

    return check


def submit_to_solr(records: list, cfg: dict) -> bool:
    solr_idx_core = cfg["solr"]["indexing_core"]
    return _submit_to_solr(records, cfg, solr_idx_core)


def _submit_to_solr(records: list, cfg: dict, core: str) -> bool:
    """
    Submits a set of records to a Solr server.

    :param records: A list of Solr records to index
    :param cfg a config object
    :return: True if successful, false if not.
    """
    solr_address = cfg["solr"]["server"]
    solr_idx_server: str = f"{solr_address}/{core}"
    log.debug("Indexing records to Solr")
    res = httpx.post(
        f"{solr_idx_server}/update",
        content=ujson.dumps(records),
        headers={"Content-Type": "application/json"},
        timeout=None,  # noqa: S113
        verify=False,  # noqa: S501
    )

    if 200 <= res.status_code < 400:
        log.debug("Indexing was successful")
        return True

    log.error("Could not index to Solr. %s: %s", res.status_code, res.text)

    return False


def empty_solr_core(cfg: dict) -> bool:
    idx_core = cfg["solr"]["indexing_core"]
    return _empty_solr_core(cfg, idx_core)


def _empty_solr_core(cfg: dict, core: str) -> bool:
    solr_address = cfg["solr"]["server"]
    solr_idx_server: str = f"{solr_address}/{core}"

    res = httpx.post(
        f"{solr_idx_server}/update?commit=true",
        content=ujson.dumps({"delete": {"query": "*:*"}}),
        headers={"Content-Type": "application/json"},
        timeout=None,  # noqa: S113
        verify=False,  # noqa: S501
    )

    if 200 <= res.status_code < 400:
        log.debug("Deletion was successful")
        return True
    return False


def format_person_name(p: dict) -> str:
    early_pfx = ""
    late_pfx = ""
    if p.get("earliest_year_approximate"):
        early_pfx = "ca. "
    if p.get("latest_year_approximate"):
        late_pfx = "ca. "
    early_year = f"{p['earliest_year']}" if p.get("earliest_year") else ""
    late_year = f"{p['latest_year']}" if p.get("latest_year") else ""

    date_str = ""
    if early_year or late_year:
        date_str = f"{early_pfx}{early_year}–{late_pfx}{late_year}"
    elif p.get("floruit"):
        date_str = f"fl. {p['floruit']}"

    if p.get("first_name"):
        name_str = f"{p['last_name']}, {p['first_name']}"
    else:
        name_str = f"{p['last_name']}"

    if date_str:
        return f"{name_str} ({date_str})"
    else:
        return name_str


def commit_changes(cfg: dict) -> bool:
    solr_idx_core = cfg["solr"]["indexing_core"]
    return _commit_changes(cfg, solr_idx_core)


def _commit_changes(cfg: dict, core: str) -> bool:
    solr_address = cfg["solr"]["server"]
    solr_idx_server: str = f"{solr_address}/{core}"
    res = httpx.get(f"{solr_idx_server}/update?commit=true", timeout=None, verify=False)  # noqa: S113, S501
    if 200 <= res.status_code < 400:
        log.debug("Commit was successful")
        return True

    log.error("Could not commit to Solr. %s: %s", res.status_code, res.text)
    return False


@functools.lru_cache
def process_composers(
    composers_str: Optional[str], unatt_composers_str: Optional[str]
) -> list[tuple[str, Optional[int], Optional[bool]]]:
    """
    Returns an array of composer names, PK, and certainty.
    """
    c = ujson.loads(composers_str) if composers_str else []
    u = ujson.loads(unatt_composers_str) if unatt_composers_str else []
    all_composers = c + u

    res = []
    for composer in all_composers:
        formatted_name = format_person_name(composer)
        res.append((formatted_name, composer["id"], composer["uncertain"]))

    return res


@functools.lru_cache
def process_sources(sources_str=Optional[str]) -> list[tuple[str, str]]:
    sources = ujson.loads(sources_str) if sources_str else []
    return sorted([(s["id"], s["display_name"]) for s in sources], key=itemgetter(1))


def swap_cores(cfg: dict) -> bool:
    """
    Swaps the index and live cores after indexing.

    :param server_address: The Solr server address
    :param index_core: The core that contains the newest index
    :param live_core: The core that is currently running the service
    :return: True if swap was successful; otherwise False
    """
    server_address = cfg["solr"]["server"]
    indexing_core = cfg["solr"]["indexing_core"]
    live_core = cfg["solr"]["live_core"]
    admconn = httpx.get(
        f"{server_address}/admin/cores?action=SWAP&core={indexing_core}&other={live_core}",
        timeout=None,  # noqa: S113
        verify=False,  # noqa: S501
    )

    if 200 <= admconn.status_code < 400:
        log.info("Core swap for %s and %s was successful.", indexing_core, live_core)
        return True

    log.error(
        "Core swap for %s and %s was not successful. Status: %s, Message: %s",
        indexing_core,
        live_core,
        admconn.status_code,
        admconn.text,
    )

    return False


def reload_core(server_address: str, core_name: str) -> bool:
    """
    Performs a core reload. This is a brute-force method of ensuring the core is current, since
    simply committing it doesn't seem to always work at the end of indexing.

    :param server_address: The Solr server address
    :param core_name: The name of the core to reload.
    :return: True if the reload was successful, otherwise False.
    """
    admconn = httpx.get(
        f"{server_address}/admin/cores?action=RELOAD&core={core_name}",
        timeout=None,  # noqa: S113
        verify=False,  # noqa: S501
    )

    if 200 <= admconn.status_code < 400:
        log.info("Core reload for %s was successful.", core_name)
        return True

    log.error(
        "Core reload for %s was not successful. Status: %s", core_name, admconn.text
    )
    return False
