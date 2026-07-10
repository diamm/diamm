from __future__ import annotations

from unittest.mock import patch

from django.contrib.sites.models import Site
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from model_bakery import baker


@override_settings(
    DIAMM_IMAGE_SERVER="https://images.example.test",
    SECRET_KEY="test-secret-key",
)
class ImageAuthTests(TestCase):
    def setUp(self) -> None:
        Site.objects.update_or_create(
            id=1,
            defaults={"domain": "testserver", "name": "testserver"},
        )
        image_type = baker.make("diamm_data.ImageType", id=1, name="Primary")
        self.user = baker.make("diamm_site.CustomUserModel", is_active=True)
        self.image = baker.make(
            "diamm_data.Image",
            type=image_type,
            location="/iiif/ms-123/page-1",
        )

    def test_authenticated_session_succeeds_for_info_json_and_tile_requests(self) -> None:
        self.client.force_login(self.user)

        info_response = self.client.get(
            reverse("protected-image-auth"),
            HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
        )
        tile_response = self.client.get(
            reverse("protected-image-auth"),
            HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/full/512,/0/default.jpg",
        )

        self.assertEqual(info_response.status_code, 204)
        self.assertEqual(
            info_response["X-DIAMM-Backend-URI"],
            "https://images.example.test/iiif/ms-123/page-1/info.json",
        )
        self.assertEqual(tile_response.status_code, 204)
        self.assertEqual(
            tile_response["X-DIAMM-Backend-URI"],
            "https://images.example.test/iiif/ms-123/page-1/full/512,/0/default.jpg",
        )

    def test_public_cover_backend_returns_low_res_backend_uri(self) -> None:
        response = self.client.get(
            reverse("cover-image-backend"),
            HTTP_X_ORIGINAL_URI=f"/cover/{self.image.pk}/",
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            response["X-DIAMM-Backend-URI"],
            "https://images.example.test/iiif/ms-123/page-1/full/400,/0/default.jpg",
        )

    def test_public_cover_backend_rejects_non_cover_paths(self) -> None:
        response = self.client.get(
            reverse("cover-image-backend"),
            HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
        )

        self.assertEqual(response.status_code, 403)

    def test_anonymous_request_is_rejected(self) -> None:
        response = self.client.get(
            reverse("protected-image-auth"),
            HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
        )

        self.assertEqual(response.status_code, 401)

    def test_inactive_user_is_rejected(self) -> None:
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("protected-image-auth"),
            HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
        )

        self.assertEqual(response.status_code, 401)

    def test_image_location_queries_db_on_each_request(self) -> None:
        self.client.force_login(self.user)

        with CaptureQueriesContext(connection) as ctx:
            first_response = self.client.get(
                reverse("protected-image-auth"),
                HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
            )
            second_response = self.client.get(
                reverse("protected-image-auth"),
                HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
            )

        self.assertEqual(first_response.status_code, 204)
        self.assertEqual(second_response.status_code, 204)
        self.assertEqual(
            sum(
                'FROM "diamm_data_image"' in query["sql"]
                for query in ctx.captured_queries
            ),
            2,
        )

    def test_image_location_lookup_uses_single_db_query(self) -> None:
        self.client.force_login(self.user)

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(
                reverse("protected-image-auth"),
                HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
            )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            sum(
                'FROM "diamm_data_image"' in query["sql"]
                for query in ctx.captured_queries
            ),
            1,
        )

    def test_protected_image_auth_does_not_lookup_diammtoken_or_solr(self) -> None:
        self.client.force_login(self.user)

        with (
            patch(
                "diamm.models.diamm_token.DiammToken.objects.select_related",
                side_effect=AssertionError("DiammToken lookup should not occur"),
            ),
            patch(
                "diamm.helpers.solr_helpers.SolrConnection.search",
                side_effect=AssertionError("Solr lookup should not occur"),
            ),
        ):
            response = self.client.get(
                reverse("protected-image-auth"),
                HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
            )

        self.assertEqual(response.status_code, 204)
