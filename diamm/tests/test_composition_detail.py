from unittest.mock import patch

from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker


class EmptySolrManager:
    results: list[dict] = []

    def search(self, *_args, **_kwargs) -> None:
        pass


class CompositionDetailDateTests(TestCase):
    def setUp(self) -> None:
        Site.objects.create(domain="testserver", name="DIAMM tests")
        self.composition = baker.make("diamm_data.Composition", title="Kyrie")
        archive = baker.make("diamm_data.Archive", siglum="GB-Lbl")
        dated_source = baker.make(
            "diamm_data.Source",
            archive=archive,
            shelfmark="Add. MS 1",
            date_statement="c. 1450",
            public=True,
            sort_order=1,
        )
        undated_source = baker.make(
            "diamm_data.Source",
            archive=archive,
            shelfmark="Add. MS 2",
            date_statement="",
            public=True,
            sort_order=2,
        )
        baker.make(
            "diamm_data.Item",
            composition=self.composition,
            source=dated_source,
            source_attribution="Attributed",
        )
        baker.make(
            "diamm_data.Item",
            composition=self.composition,
            source=undated_source,
            source_attribution="Anonymous",
        )
        self.url = reverse("composition-detail", kwargs={"pk": self.composition.pk})

    @patch("diamm.serializers.website.composition.SolrManager", EmptySolrManager)
    def test_json_sources_include_date_statement(self) -> None:
        response = self.client.get(self.url, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        sources = response.json()["sources"]
        self.assertEqual(sources[0]["date_statement"], "c. 1450")
        self.assertNotIn("date_statement", sources[1])

    @patch("diamm.serializers.website.composition.SolrManager", EmptySolrManager)
    def test_html_displays_source_dates_and_fallback(self) -> None:
        response = self.client.get(self.url, HTTP_ACCEPT="text/html")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<th>Date</th>", html=True)
        self.assertContains(response, "c. 1450")
        self.assertContains(response, "Attributed")
        self.assertContains(response, "Anonymous")
        self.assertContains(response, "<td>-</td>", html=True)
