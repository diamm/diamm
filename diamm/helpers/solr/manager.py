import logging
from collections.abc import Iterator

from django.conf import settings

from diamm.helpers.solr.client import DEFAULT_SOLR_CLIENT, SolrClient

log = logging.getLogger(__name__)


class SolrManager:
    """
    Manages a Solr connection, allowing seamless iteration through paginated results:

        >>> m = SolrManager()
        >>> m.search("*:*", fq=["type:something"], sort="some_i asc")
        >>> for r in m.results:
        ...     print(r)

    This will manage fetching the next page and results when needed. This class uses the cursorMark
    function, which returns a 'nextCursorMark' in the results objects to fetch the next page of results.
    Cursor marks are described in detail here:

    https://lucene.apache.org/solr/guide/7_1/pagination-of-results.html#fetching-a-large-number-of-sorted-results-cursors

    When calling the `.search()` method you should omit two parameters: `cursorMark` and a sort on
    the unique key (controlled using the SORT_STATEMENT parameter above). This will be added into the call prior
    to sending the query to Solr. The result object is managed by this class privately.

    Once `search()` has been called users can iterate through the `results` property and it will transparently
    fire off requests for the next page (technically, the next cursor mark) before yielding a result.
    """

    def __init__(
        self,
        client: SolrClient | None = None,
        curs_sort_statement: str = "id asc",
    ) -> None:
        self.client = client or DEFAULT_SOLR_CLIENT
        self._res = None
        self._curs_sort_statement: str = curs_sort_statement
        self._hits: int = 0
        self.docs: list[dict] = []
        self._q: str | None = None
        self._q_kwargs: dict = {}
        self._cursorMark: str = "*"
        self._idx: int = 0
        self._page_idx: int = 0
        # since group queries don't use cursor marks, we need to manually manage
        # the number of rows we return in the iterator
        self._group_rows: int = settings.SOLR["PAGE_SIZE"]
        self._gp_kwargs: dict = {
            "group": "true",
            "group.limit": 1000,
            "group.ngroups": "true",
        }
        self._group_name: str = ""

    def search(self, q: str, **kwargs) -> None:
        """
        Searches Solr with additional housekeeping that manages the results object
        and stores the query parameters for transparently fetching pages.
        :param q: A default query parameter for Solr
        :param kwargs: Keyword arguments to pass along to SolrClient.raw_search
        :return: None
        """
        self._q = q
        self._q_kwargs = kwargs
        self._idx = 0
        self._page_idx = 0

        if "sort" in kwargs:
            self._q_kwargs["sort"] += f", {self._curs_sort_statement}"
        else:
            self._q_kwargs["sort"] = f"{self._curs_sort_statement}"

        self._cursorMark = "*"
        self._q_kwargs["cursorMark"] = self._cursorMark
        self._res = self.client.raw_search(q, **self._q_kwargs)
        self._hits = self._res.hits
        self.docs = self._res.docs

    @property
    def first(self) -> dict | None:
        if len(self.docs) == 0:
            return None
        return self.docs[0]

    @property
    def hits(self) -> int:
        """
        Returns the number of hits found in response to a search.
        :return: Number of hits
        """
        if self._res is None:
            log.warning(
                "A request for number of results was called before a search was initiated"
            )

        return self._hits

    def grouped_search(
        self, group_name: str, group_sort: str, q: str, **kwargs
    ) -> None:
        self._idx = 0
        self._page_idx = 0
        self._q = q
        self._q_kwargs = kwargs
        self._group_name = group_name
        self._gp_kwargs.update(
            {"group.field": self._group_name, "group.sort": group_sort}
        )
        self._res = self.client.raw_search(
            q, start=0, rows=self._group_rows, **self._q_kwargs, **self._gp_kwargs
        )
        self._hits = self._res.hits

    @property
    def grouped_results(self) -> Iterator[dict]:
        if self._res is None:
            log.warning(
                "A request for a group was called before a search was initiated"
            )

        group: dict = self._res.grouped.get(self._group_name)
        num_groups: int = group["ngroups"]
        pgno = 0

        while self._idx < num_groups:
            try:
                yield self._res.grouped.get(self._group_name)["groups"][self._page_idx]
            except IndexError:
                self._page_idx = 0
                # When we run out
                # of results on the page, we'll trigger a new
                # page load, which we can compute by taking the
                # page number (assuming page 0 start), incrementing by 1, and then multiplying by
                # the number of rows we should retrieve. On the first
                # round, we'll start at 0, then the next will start at 21, and then
                # 41, and then 61, etc.
                pgno += 1
                start: int = pgno * self._group_rows

                self._res = self.client.raw_search(
                    self._q,
                    start=start,
                    rows=self._group_rows,
                    **self._q_kwargs,
                    **self._gp_kwargs,
                )

                gp = self._res.grouped.get(self._group_name)
                if gp and gp.get("groups"):
                    yield gp.get("groups")[self._page_idx]
                else:
                    break

            self._idx += 1
            self._page_idx += 1

    @property
    def results(self) -> Iterator[dict]:
        """
        Provides a generator for Solr result documents, yielding
        the next result on every loop. In the case where the next result
        is on the next page, it will fetch the next page before yielding
        the first result on that page.
        :return: The full list of Solr results
        """
        if self._res is None:
            log.warning(
                "A request for results was called before a search was initiated."
            )

        while self._idx < self._hits:
            try:
                yield self._res.docs[self._page_idx]
            except IndexError:
                self._page_idx = 0
                self._cursorMark = self._res.nextCursorMark
                self._q_kwargs["cursorMark"] = self._res.nextCursorMark
                self._res = self.client.raw_search(self._q, **self._q_kwargs)
                self._hits = self._res.hits
                if self._res.docs:
                    yield self._res.docs[self._page_idx]
                else:
                    break

            self._page_idx += 1
            self._idx += 1
