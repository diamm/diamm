from typing import Any
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.core import signing
from django.urls import reverse

AUTH_CONTEXT = "http://iiif.io/api/auth/2/context.json"
TOKEN_SALT = "diamm.iiif-auth-token"  # noqa: S105


def get_token_max_age() -> int:
    return int(getattr(settings, "IIIF_AUTH_TOKEN_MAX_AGE", 300))


def make_access_token(user_id: int) -> str:
    return signing.dumps({"user_id": user_id}, salt=TOKEN_SALT)


def load_access_token(token: str) -> dict[str, Any]:
    return signing.loads(token, salt=TOKEN_SALT, max_age=get_token_max_age())


def is_valid_origin(origin: str | None) -> bool:
    if not origin:
        return False

    parsed = urlsplit(origin)
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
        and not parsed.path
        and not parsed.query
        and not parsed.fragment
    )


def language_map(value: str) -> dict[str, list[str]]:
    return {"en": [value]}


def absolute_reverse(request, viewname: str) -> str:
    return request.build_absolute_uri(reverse(viewname))


def build_auth_probe_service(
    request, resource_uri: str | None = None
) -> dict[str, Any]:
    probe_id = absolute_reverse(request, "iiif-auth-probe")
    if resource_uri:
        probe_id = f"{probe_id}?{urlencode({'uri': resource_uri})}"

    return {
        "@context": AUTH_CONTEXT,
        "id": probe_id,
        "type": "AuthProbeService2",
        "errorHeading": language_map("Login required"),
        "errorNote": language_map("Log in to DIAMM to view this image."),
        "service": [build_auth_access_service(request)],
    }


def build_auth_access_service(request) -> dict[str, Any]:
    return {
        "id": absolute_reverse(request, "iiif-auth-access"),
        "type": "AuthAccessService2",
        "profile": "active",
        "label": language_map("Login to DIAMM"),
        "heading": language_map("Login required"),
        "note": language_map("DIAMM requires that you log in to view this image."),
        "confirmLabel": language_map("Log in"),
        "service": [
            {
                "id": absolute_reverse(request, "iiif-auth-token"),
                "type": "AuthAccessTokenService2",
                "errorHeading": language_map("Unable to authorize image access"),
                "errorNote": language_map("Log in to DIAMM and try again."),
            },
            {
                "id": absolute_reverse(request, "iiif-auth-logout"),
                "type": "AuthLogoutService2",
                "label": language_map("Log out of DIAMM"),
            },
        ],
    }


def add_auth_service(info_json: dict[str, Any], auth_service: dict[str, Any]) -> None:
    existing = info_json.get("service")
    if existing is None:
        info_json["service"] = [auth_service]
        return

    services = existing if isinstance(existing, list) else [existing]
    if not any(service.get("type") == "AuthProbeService2" for service in services):
        services.append(auth_service)

    info_json["service"] = services
