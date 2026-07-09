import urllib.parse
from collections.abc import Iterator
from datetime import timedelta

from django.conf import settings
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect
from pyreqwest.client import SyncClient, SyncClientBuilder
from pyreqwest.exceptions import ConnectError, PyreqwestError
from pyreqwest.response import SyncResponse
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated

from diamm.authentication import DiammTokenAuthentication
from diamm.helpers.solr_helpers import SolrConnection

IMAGE_PROXY_CLIENT: SyncClient = (
    SyncClientBuilder().connect_timeout(timedelta(seconds=2)).build()
)


def cover_image_serve(request: HttpRequest, pk: str | int) -> HttpResponse:
    # allow unauthenticated access, but hardcode the image parameters so that
    # the high-res image cannot be downloaded
    return _image_lookup(request, pk, region="full", size="400,", rotation="0")


def image_serve_redirect(request: HttpRequest, pk: str | int) -> HttpResponse:
    return HttpResponseRedirect(
        urllib.parse.urljoin(request.path, "info.json"),
        status=status.HTTP_303_SEE_OTHER,
    )


@api_view(["GET", "OPTIONS"])
@authentication_classes([DiammTokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def image_serve(
    request: HttpRequest,
    pk: str | int,
    region: str | None = None,
    size: str | None = None,
    rotation: str | None = None,
    *args: object,
    **kwargs: object,
) -> HttpResponse:
    """
    This serves as a consistent proxy for all image locations
    in DIAMM. The reason for this is twofold:

    1) Same-origin requests. All images should be served from the same
    origin so that we don't get problems with security restrictions in
    browsers, especially for tainted canvas.

    2) Since DIAMM will be HTTPS, and since not every external provider will
    provide HTTPS, we will get problems with browsers not loading insecure content.

    The images are requested via their database PK, but since we don't necessarily
    want to bother Postgres for this (slow lookup) we'll ask Solr for it.
    """
    return _image_lookup(request, pk, region, size, rotation)


def _image_lookup(
    request: HttpRequest,
    pk: str | int,
    region: str | None = None,
    size: str | None = None,
    rotation: str | None = None,
) -> HttpResponse:
    field_list = ["location_s"]
    # conn = pysolr.Solr(settings.SOLR['SERVER'])
    req = SolrConnection.search(
        "*:*", fq=["type:image", f"pk:{pk}"], fl=field_list, rows=1
    )  # ensure only one result is returned

    if req.hits == 0:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    result = req.docs[0]
    location: str | None = result.get("location_s")
    if not location or location == "None":
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    referer: str = f"{request.scheme}://{request.get_host()}"
    if region and size and rotation:
        location += f"/{region}/{size}/{rotation}/default.jpg"
    elif not location.endswith("/info.json"):
        location += "/info.json"

    full_location = f"{settings.DIAMM_IMAGE_SERVER}{location}"
    iiif_id = request.META.get("HTTP_X_IIIF_ID")
    headers: dict[str, str | None] = {
        "referer": referer,
        "X-DIAMM": settings.DIAMM_IMAGE_KEY,
        "X-IIIF-ID": iiif_id,
        "User-Agent": settings.DIAMM_UA,
    }
    req_headers: dict[str, str] = {k: v for k, v in headers.items() if v is not None}

    try:
        request_builder = (
            IMAGE_PROXY_CLIENT.get(full_location)
            .headers(req_headers)
            .timeout(timedelta(seconds=10))
            .build_streamed()
        )
        with request_builder as response:
            if response.status == 200:
                content_type = response.get_header("content-type")
                return HttpResponse(
                    _stream_response_bytes(response),
                    content_type=content_type,
                )
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except (ConnectError, PyreqwestError):
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _stream_response_bytes(response: SyncResponse) -> Iterator[bytes]:
    while chunk := response.body_reader.read_chunk():
        yield bytes(chunk)
