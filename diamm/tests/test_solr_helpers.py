from unittest.mock import MagicMock, call

from django.test import SimpleTestCase

from diamm.helpers.solr import SolrManager, SolrSearchResult


def result(
    docs=None, *, hits=0, grouped=None, next_cursor_mark=None
) -> SolrSearchResult:
    return SolrSearchResult(
        docs=docs or [],
        hits=hits,
        facets={},
        raw_response={},
        grouped=grouped or {},
        nextCursorMark=next_cursor_mark,
    )


class SolrManagerTest(SimpleTestCase):
    def test_search_appends_cursor_sort(self) -> None:
        client = MagicMock()
        client.raw_search.return_value = result()
        manager = SolrManager(client=client)

        manager.search("*:*", fq=["type:source"], sort="shelfmark_ans asc")

        client.raw_search.assert_called_once_with(
            "*:*",
            fq=["type:source"],
            sort="shelfmark_ans asc, id asc",
            cursorMark="*",
        )

    def test_results_fetch_subsequent_cursor_page(self) -> None:
        client = MagicMock()
        client.raw_search.side_effect = [
            result([{"id": "1"}], hits=2, next_cursor_mark="next"),
            result([{"id": "2"}], hits=2, next_cursor_mark="done"),
        ]
        manager = SolrManager(client=client)

        manager.search("*:*", rows=1)

        self.assertEqual(list(manager.results), [{"id": "1"}, {"id": "2"}])
        self.assertEqual(client.raw_search.call_count, 2)
        self.assertEqual(client.raw_search.call_args_list[1].kwargs["cursorMark"], "next")

    def test_grouped_results_fetch_subsequent_page(self) -> None:
        first_group = {"ngroups": 2, "groups": [{"groupValue": "one"}]}
        second_group = {"ngroups": 2, "groups": [{"groupValue": "two"}]}
        client = MagicMock()
        client.raw_search.side_effect = [
            result(hits=2, grouped={"source_i": first_group}),
            result(hits=2, grouped={"source_i": second_group}),
        ]
        manager = SolrManager(client=client)
        manager._group_rows = 1

        manager.grouped_search("source_i", "id asc", "*:*", fq=["type:item"])

        self.assertEqual(
            list(manager.grouped_results),
            [{"groupValue": "one"}, {"groupValue": "two"}],
        )
        self.assertEqual(
            client.raw_search.call_args_list,
            [
                call(
                    "*:*",
                    start=0,
                    rows=1,
                    fq=["type:item"],
                    group="true",
                    **{
                        "group.limit": 1000,
                        "group.ngroups": "true",
                        "group.field": "source_i",
                        "group.sort": "id asc",
                    },
                ),
                call(
                    "*:*",
                    start=1,
                    rows=1,
                    fq=["type:item"],
                    group="true",
                    **{
                        "group.limit": 1000,
                        "group.ngroups": "true",
                        "group.field": "source_i",
                        "group.sort": "id asc",
                    },
                ),
            ],
        )
