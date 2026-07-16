import json
import logging
import re
import urllib.parse
from typing import Any

import requests
from django.conf import settings
from django.contrib.auth import logout
from django.core import signing
from django.http import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from diamm.iiif_auth import (
    AUTH_CONTEXT,
    add_auth_service,
    build_auth_probe_service,
    get_token_max_age,
    is_valid_origin,
    load_access_token,
    make_access_token,
)
from diamm.models import CustomUserModel
from diamm.models.data.image import Image

log = logging.getLogger("diamm")
COVER_IMAGE_SUFFIX = "/full/400,/0/default.jpg"


# These placeholder views exist only so Django can reverse the canonical public
# and protected image URLs. In supported environments, Nginx owns those paths.
def cover_image(_request: HttpRequest, pk: int) -> HttpResponse:
    del pk
    return HttpResponse(status=status.HTTP_501_NOT_IMPLEMENTED)


def image_serve_redirect(_request: HttpRequest, pk: int) -> HttpResponse:
    del pk
    return HttpResponse(status=status.HTTP_501_NOT_IMPLEMENTED)


def image_serve_info(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "OPTIONS":
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    location = _get_image_location(pk)
    if not location:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    info_json = _fetch_iip_info_json(request, pk, location)
    if info_json is None:
        return HttpResponse(status=status.HTTP_502_BAD_GATEWAY)

    public_info_uri = request.build_absolute_uri(
        reverse("image-serve-info", kwargs={"pk": pk})
    )
    add_auth_service(info_json, build_auth_probe_service(request, public_info_uri))

    return JsonResponse(info_json)


def image_serve(_request: HttpRequest, pk: int, suffix: str) -> HttpResponse:
    del pk, suffix
    return HttpResponse(status=status.HTTP_501_NOT_IMPLEMENTED)


@never_cache
def iiif_auth_access(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        next_query = urllib.parse.urlencode({"next": request.get_full_path()})
        return redirect(f"{reverse('login')}?{next_query}")

    return HttpResponse(
        """<!doctype html>
<html>
<head><title>DIAMM image access authorized</title></head>
<body>
<p>DIAMM image access authorized. You can close this window.</p>
<script>window.close();</script>
</body>
</html>""",
        content_type="text/html",
    )


@never_cache
@xframe_options_exempt
def iiif_auth_token(request: HttpRequest) -> HttpResponse:
    message_id = request.GET.get("messageId", "")
    origin = request.GET.get("origin")

    if not message_id:
        message = _auth_token_error("invalidRequest", message_id)
        target_origin = origin if is_valid_origin(origin) else "*"
    elif not is_valid_origin(origin):
        message = _auth_token_error("invalidOrigin", message_id)
        target_origin = "*"
    elif not request.user.is_authenticated:
        message = _auth_token_error("missingAspect", message_id)
        target_origin = origin
    elif not isinstance(request.user, CustomUserModel) or not request.user.is_active:
        message = _auth_token_error("invalidAspect", message_id)
        target_origin = origin
    else:
        message = {
            "@context": AUTH_CONTEXT,
            "type": "AuthAccessToken2",
            "accessToken": make_access_token(request.user.pk),
            "expiresIn": get_token_max_age(),
            "messageId": message_id,
        }
        target_origin = origin

    return HttpResponse(
        f"""<!doctype html>
<html>
<body>
<script>
window.parent.postMessage({json.dumps(message)}, {json.dumps(target_origin)});
</script>
</body>
</html>""",
        content_type="text/html",
    )


def iiif_auth_probe(request: HttpRequest) -> HttpResponse:
    if request.method == "OPTIONS":
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    user = request.user
    if user.is_authenticated:
        probe_status = (
            status.HTTP_200_OK if user.is_active else status.HTTP_403_FORBIDDEN
        )
    else:
        probe_status = status.HTTP_401_UNAUTHORIZED

    if probe_status == status.HTTP_401_UNAUTHORIZED and auth_header.startswith(
        "Bearer "
    ):
        token = auth_header.removeprefix("Bearer ").strip()
        try:
            token_data = load_access_token(token)
            user = CustomUserModel.objects.get(pk=token_data.get("user_id"))
        except (
            CustomUserModel.DoesNotExist,
            signing.BadSignature,
            signing.SignatureExpired,
        ):
            probe_status = status.HTTP_401_UNAUTHORIZED
        else:
            probe_status = (
                status.HTTP_200_OK if user.is_active else status.HTTP_403_FORBIDDEN
            )

    return JsonResponse(
        {
            "@context": AUTH_CONTEXT,
            "type": "AuthProbeResult2",
            "status": probe_status,
        }
    )


@never_cache
def iiif_auth_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponse(
        """<!doctype html>
<html>
<head><title>Logged out of DIAMM</title></head>
<body>
<p>You have been logged out of DIAMM. You can close this window.</p>
<script>window.close();</script>
</body>
</html>""",
        content_type="text/html",
    )


@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([])
def protected_image_auth(request: HttpRequest) -> HttpResponse:
    user = request.user
    if not request.user.is_authenticated:
        log.debug("Protected image auth rejected: anonymous request")
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if not isinstance(user, CustomUserModel) or not user.is_active:
        log.debug(
            "Protected image auth rejected: inactive or invalid user id=%s",
            getattr(user, "pk", None),
        )
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    original_uri = request.META.get("HTTP_X_ORIGINAL_URI") or request.GET.get("uri")
    if not original_uri:
        log.debug(
            "Protected image auth rejected: missing original URI for user id=%s",
            user.pk,
        )
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    backend_query = _resolve_backend_query_from_request_path(original_uri)
    if not backend_query:
        log.debug(
            "Protected image auth rejected: no backend query for user id=%s original_uri=%s",
            user.pk,
            original_uri,
        )
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    log.debug(
        "Protected image auth ok: user id=%s original_uri=%s backend_query=%s",
        user.pk,
        original_uri,
        backend_query,
    )
    response = HttpResponse(status=status.HTTP_204_NO_CONTENT)
    response["X-DIAMM-Backend-Query"] = backend_query
    return response


def public_image_auth(request: HttpRequest) -> HttpResponse:
    original_uri = request.META.get("HTTP_X_ORIGINAL_URI") or request.GET.get("uri")
    if not original_uri:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    if not urllib.parse.urlsplit(original_uri).path.startswith("/cover/"):
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    backend_query = _resolve_backend_query_from_request_path(original_uri)
    if not backend_query:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    response = HttpResponse(status=status.HTTP_204_NO_CONTENT)
    response["X-DIAMM-Backend-Query"] = backend_query
    return response


def _auth_token_error(profile: str, message_id: str) -> dict[str, Any]:
    return {
        "@context": AUTH_CONTEXT,
        "type": "AuthAccessTokenError2",
        "profile": profile,
        "messageId": message_id,
        "heading": {"en": ["Unable to authorize image access"]},
        "note": {"en": ["Log in to DIAMM and try again."]},
    }


def _fetch_iip_info_json(
    request: HttpRequest, pk: int, location: str
) -> dict[str, Any] | None:
    del pk
    info_url = f"{settings.DIAMM_IMAGE_SERVER}{location}/info.json"
    headers = {
        "referer": f"https://{settings.HOSTNAME}",
        "X-IIIF-ID": request.build_absolute_uri(request.path).removesuffix(
            "/info.json"
        ),
    }
    if image_key := getattr(settings, "DIAMM_IMAGE_KEY", None):
        headers["X-DIAMM"] = image_key

    try:
        response = requests.get(info_url, headers=headers, timeout=10)
        response.raise_for_status()
        info_json = response.json()
    except requests.RequestException, ValueError:
        log.exception("Could not fetch IIP info.json for location=%s", location)
        return None

    if not isinstance(info_json, dict):
        log.warning("IIP info.json was not a JSON object for location=%s", location)
        return None

    return info_json


def _get_image_location(pk: int | str) -> str | None:
    try:
        location = (
            Image.objects.only("location").values_list("location", flat=True).get(pk=pk)
        )
    except Image.DoesNotExist:
        return None

    if not location or location == "None":
        return None

    return location


def _resolve_backend_query_from_request_path(request_path: str) -> str | None:
    path = urllib.parse.urlsplit(request_path).path

    if path.startswith("/cover/"):
        match = re.fullmatch(r"/cover/(?P<pk>\d+)/", path)
        suffix = COVER_IMAGE_SUFFIX
    elif path.startswith("/images/"):
        match = re.fullmatch(r"/images/(?P<pk>\d+)/(?P<suffix>.+)", path)
        if not match:
            return None

        suffix = f"/{match.group('suffix')}"
        if not suffix.endswith(("/info.json", "/default.jpg")):
            return None
    else:
        return None

    if not match:
        return None

    location = _get_image_location(match.group("pk"))
    if not location:
        return None

    return f"IIIF={location}{suffix}"
