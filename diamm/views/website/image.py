import urllib.parse
from typing import Optional

import httpx
from django.conf import settings
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect
from rest_framework import status

from diamm.helpers.solr_helpers import SolrConnection

client = httpx.Client()


def cover_image_serve(request: HttpRequest, pk) -> HttpResponse:
    # allow unauthenticated access, but hardcode the image parameters so that
    # the high-res image cannot be downloaded
    print("cover request", pk)
    return _image_lookup(request, pk, region="full", size="400,", rotation="0")


def image_serve_redirect(request: HttpRequest, pk) -> HttpResponse:
    return HttpResponseRedirect(
        urllib.parse.urljoin(request.path, "info.json"),
        status=status.HTTP_303_SEE_OTHER,
    )


def image_serve(
    request,
    pk,
    region: str = None,
    size: str = None,
    rotation: str = None,
    *args,
    **kwargs,
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
    if not request.user:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    return _image_lookup(request, pk, region, size, rotation)


def _image_lookup(
    request: HttpRequest, pk, region=None, size=None, rotation=None
) -> HttpResponse:
    field_list = ["location_s"]
    # conn = pysolr.Solr(settings.SOLR['SERVER'])
    req = SolrConnection.search(
        "*:*", fq=["type:image", f"pk:{pk}"], fl=field_list, rows=1
    )  # ensure only one result is returned

    print(req.hits)

    if req.hits == 0:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    result = req.docs[0]
    location: Optional[str] = result.get("location_s")
    if not location or location == "None":
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    referer: str = f"{request.scheme}://{request.get_host()}"
    if region and size and rotation:
        location: str = f"{location}/{region}/{size}/{rotation}/default.jpg"
    elif not location.endswith("/info.json"):
        location += "/info.json"

    full_location = f"{settings.DIAMM_IMAGE_SERVER}/iip/iipsrv.fcgi?IIIF={location}"
    print(full_location)
    iiif_id = request.META.get("HTTP_X_IIIF_ID")
    headers: dict = {
        "referer": referer,
        "X-DIAMM": settings.DIAMM_IMAGE_KEY,
        "X-IIIF-ID": iiif_id,
        "User-Agent": settings.DIAMM_UA,
    }

    try:
        with client.stream("GET", full_location, headers=headers, timeout=10) as r:
            if r.status_code == 200:
                return HttpResponse(
                    r.iter_raw(), content_type=r.headers["content-type"]
                )
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except httpx.ConnectError:
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
