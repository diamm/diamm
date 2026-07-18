from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIRequestFactory

from diamm.serializers.website.composition import CompositionDetailSerializer
from diamm.views.website.composition import CompositionDetail


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
        self.assertContains(response, "<th>Source Date</th>", html=True)
        self.assertContains(response, "c. 1450")
        self.assertContains(response, "Attributed")
        self.assertContains(response, "Anonymous")
        self.assertContains(response, "<td>-</td>", html=True)

    @patch("diamm.serializers.website.composition.SolrManager", EmptySolrManager)
    def test_external_edition_links_appear_in_json_and_html(self) -> None:
        baker.make(
            "diamm_data.CompositionURL",
            composition=self.composition,
            type=1,
            link="https://1520s-project.example/work/Any1001a",
            link_text="Kyrie from the Missa Vulnerasti cor meum",
        )

        json_response = self.client.get(self.url, HTTP_ACCEPT="application/json")
        self.assertEqual(
            json_response.json()["links"],
            [
                {
                    "type": "Edition",
                    "link_text": "Kyrie from the Missa Vulnerasti cor meum",
                    "link": "https://1520s-project.example/work/Any1001a",
                }
            ],
        )

        html_response = self.client.get(self.url, HTTP_ACCEPT="text/html")
        self.assertContains(html_response, "External editions and scores")
        self.assertContains(html_response, "Kyrie from the Missa Vulnerasti cor meum")
        self.assertContains(
            html_response, "https://1520s-project.example/work/Any1001a"
        )

    @patch("diamm.serializers.website.composition.SolrManager", EmptySolrManager)
    def test_serializer_reuses_view_prefetches(self) -> None:
        request = APIRequestFactory().get(self.url)
        request.user = AnonymousUser()
        view = CompositionDetail()
        view.request = request
        composition = view.get_queryset().get(pk=self.composition.pk)

        with self.assertNumQueries(0):
            content = CompositionDetailSerializer(
                composition,
                context={"request": request},
            ).serialized

        self.assertEqual(len(content["sources"]), 2)
