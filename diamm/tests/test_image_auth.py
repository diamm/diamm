from __future__ import annotations

import re
from unittest.mock import patch

from django.contrib.sites.models import Site
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from model_bakery import baker


class FakeIIPResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("upstream error")

    def json(self) -> dict:
        return self.payload


@override_settings(
    SECRET_KEY="test-secret-key",  # noqa: S106
    DIAMM_IMAGE_SERVER="https://iip.example/iipsrv.fcgi?IIIF=",
    DIAMM_IMAGE_KEY="test-image-key",
    HOSTNAME="testserver",
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
            info_response["X-DIAMM-Backend-Query"],
            "IIIF=/iiif/ms-123/page-1/info.json",
        )
        self.assertEqual(tile_response.status_code, 204)
        self.assertEqual(
            tile_response["X-DIAMM-Backend-Query"],
            "IIIF=/iiif/ms-123/page-1/full/512,/0/default.jpg",
        )

    def test_public_cover_backend_returns_low_res_backend_uri(self) -> None:
        response = self.client.get(
            reverse("cover-image-backend"),
            HTTP_X_ORIGINAL_URI=f"/cover/{self.image.pk}/",
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            response["X-DIAMM-Backend-Query"],
            "IIIF=/iiif/ms-123/page-1/full/400,/0/default.jpg",
        )

    def test_public_cover_route_is_named_and_direct_django_hit_is_not_implemented(self) -> None:
        url = reverse("cover-image", kwargs={"pk": self.image.pk})
        response = self.client.get(url)

        self.assertEqual(url, f"/cover/{self.image.pk}/")
        self.assertEqual(response.status_code, 501)

    def test_protected_image_routes_are_named_and_direct_django_tile_hits_are_not_implemented(
        self,
    ) -> None:
        redirect_url = reverse("image-serve-redirect", kwargs={"pk": self.image.pk})
        tile_url = reverse(
            "image-serve",
            kwargs={"pk": self.image.pk, "suffix": "full/512,/0/default.jpg"},
        )

        redirect_response = self.client.get(redirect_url)
        tile_response = self.client.get(tile_url)

        self.assertEqual(redirect_url, f"/images/{self.image.pk}/")
        self.assertEqual(tile_url, f"/images/{self.image.pk}/full/512,/0/default.jpg")
        self.assertEqual(redirect_response.status_code, 501)
        self.assertEqual(tile_response.status_code, 501)

    def test_image_info_json_proxies_iip_and_appends_auth_service(self) -> None:
        response_payload = {
            "@context": "http://iiif.io/api/image/2/context.json",
            "@id": "https://iip.example/iipsrv.fcgi?IIIF=/iiif/ms-123/page-1",
            "profile": "http://iiif.io/api/image/2/level1.json",
            "service": {"@id": "https://example.test/physical-dimensions"},
        }

        with patch(
            "diamm.views.website.image.requests.get",
            return_value=FakeIIPResponse(response_payload),
        ) as mocked_get:
            response = self.client.get(
                reverse("image-serve-info", kwargs={"pk": self.image.pk}),
                HTTP_ORIGIN="https://viewer.example",
            )

        self.assertEqual(response.status_code, 200)
        mocked_get.assert_called_once()
        self.assertEqual(
            mocked_get.call_args.args[0],
            "https://iip.example/iipsrv.fcgi?IIIF=/iiif/ms-123/page-1/info.json",
        )
        self.assertEqual(
            mocked_get.call_args.kwargs["headers"]["X-DIAMM"], "test-image-key"
        )
        self.assertEqual(
            response["Access-Control-Allow-Origin"], "https://viewer.example"
        )

        data = response.json()
        self.assertEqual(data["@context"], "http://iiif.io/api/image/2/context.json")
        self.assertIsInstance(data["service"], list)
        self.assertEqual(data["service"][0]["@id"], "https://example.test/physical-dimensions")

        auth_service = data["service"][1]
        self.assertEqual(auth_service["@context"], "http://iiif.io/api/auth/2/context.json")
        self.assertEqual(auth_service["type"], "AuthProbeService2")
        self.assertIn("/iiif/auth/probe/", auth_service["id"])
        self.assertEqual(auth_service["service"][0]["type"], "AuthAccessService2")
        self.assertEqual(
            auth_service["service"][0]["service"][0]["type"],
            "AuthAccessTokenService2",
        )

    def test_image_info_json_uses_service_array_without_duplicate_auth_service(self) -> None:
        response_payload = {
            "@context": "http://iiif.io/api/image/2/context.json",
            "service": [{"@id": "https://example.test/physical-dimensions"}],
        }

        with patch(
            "diamm.views.website.image.requests.get",
            return_value=FakeIIPResponse(response_payload),
        ):
            first_response = self.client.get(
                reverse("image-serve-info", kwargs={"pk": self.image.pk})
            )
            second_response = self.client.get(
                reverse("image-serve-info", kwargs={"pk": self.image.pk})
            )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        auth_services = [
            service
            for service in second_response.json()["service"]
            if service.get("type") == "AuthProbeService2"
        ]
        self.assertEqual(len(auth_services), 1)

    def test_iiif_auth_access_redirects_anonymous_users_to_login(self) -> None:
        response = self.client.get(
            reverse("iiif-auth-access"), {"origin": "https://viewer.example"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/?next=", response["Location"])

    def test_iiif_auth_access_closes_for_authenticated_users(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("iiif-auth-access"), {"origin": "https://viewer.example"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "window.close()")

    def test_iiif_auth_token_posts_access_token_for_authenticated_user(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("iiif-auth-token"),
            {"messageId": "msg-1", "origin": "https://viewer.example"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("X-Frame-Options", response)
        self.assertContains(response, "AuthAccessToken2")
        self.assertContains(response, "msg-1")

        token_match = re.search(r'"accessToken": "([^"]+)"', response.content.decode())
        self.assertIsNotNone(token_match)

        probe_response = self.client.get(
            reverse("iiif-auth-probe"),
            HTTP_AUTHORIZATION=f"Bearer {token_match.group(1)}",
            HTTP_ORIGIN="https://viewer.example",
        )
        self.assertEqual(probe_response.status_code, 200)
        self.assertEqual(probe_response.json()["status"], 200)
        self.assertEqual(
            probe_response["Access-Control-Allow-Origin"], "https://viewer.example"
        )

    def test_iiif_auth_token_posts_error_for_anonymous_user(self) -> None:
        response = self.client.get(
            reverse("iiif-auth-token"),
            {"messageId": "msg-1", "origin": "https://viewer.example"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AuthAccessTokenError2")
        self.assertContains(response, "missingAspect")

    def test_iiif_auth_probe_returns_embedded_unauthorized_status_for_invalid_token(
        self,
    ) -> None:
        response = self.client.get(
            reverse("iiif-auth-probe"),
            HTTP_AUTHORIZATION="Bearer invalid",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], 401)

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
                "diamm.helpers.solr.SolrClient.raw_search",
                side_effect=AssertionError("Solr lookup should not occur"),
            ),
        ):
            response = self.client.get(
                reverse("protected-image-auth"),
                HTTP_X_ORIGINAL_URI=f"/images/{self.image.pk}/info.json",
            )

        self.assertEqual(response.status_code, 204)
