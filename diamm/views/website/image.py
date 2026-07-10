import logging
import re
import urllib.parse
from django.http import HttpResponse
from django.http.request import HttpRequest
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
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


def image_serve_info(_request: HttpRequest, pk: int) -> HttpResponse:
    del pk
    return HttpResponse(status=status.HTTP_501_NOT_IMPLEMENTED)


def image_serve(_request: HttpRequest, pk: int, suffix: str) -> HttpResponse:
    del pk, suffix
    return HttpResponse(status=status.HTTP_501_NOT_IMPLEMENTED)


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

    try:
        location = (
            Image.objects.only("location")
            .values_list("location", flat=True)
            .get(pk=match.group("pk"))
        )
    except Image.DoesNotExist:
        return None

    if not location or location == "None":
        return None

    return f"IIIF={location}{suffix}"
