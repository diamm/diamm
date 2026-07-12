from unittest.mock import patch

from django.test import SimpleTestCase

from diamm.helpers.solr import SolrSearchResult
from diamm.serializers.iiif.service import ServiceSerializer


class ServiceSerializerVoiceTest(SimpleTestCase):
    @patch("diamm.serializers.iiif.service.SOLR_CLIENT")
    def test_get_voices_uses_solr_client(self, client) -> None:
        client.raw_search.return_value = SolrSearchResult(
            docs=[
                {
                    "voice_type_s": "Cantus",
                    "voice_text_s": None,
                    "languages_ss": ["Latin"],
                    "clef_s": "C3",
                }
            ],
            hits=1,
            facets={},
            raw_response={},
            grouped={},
        )

        voices = ServiceSerializer().get_voices({"voices_ii": [2, 5]})

        client.raw_search.assert_called_once_with(
            "*:*",
            fq=["type:voice", "{!terms f=pk}2,5"],
            sort="sort_order_i asc",
            rows=100,
        )
        self.assertEqual(
            voices,
            [{"voice_type": "Cantus", "languages": ["Latin"], "clef": "C3"}],
        )

    @patch("diamm.serializers.iiif.service.SOLR_CLIENT")
    def test_get_voices_returns_none_for_no_hits(self, client) -> None:
        client.raw_search.return_value = SolrSearchResult(
            docs=[], hits=0, facets={}, raw_response={}, grouped={}
        )

        self.assertIsNone(ServiceSerializer().get_voices({"voices_ii": [2]}))
