from typing import Dict, Optional

import requests
from diamm.helpers.solr_helpers import SolrConnection
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status


def image_serve(request, pk, region=None, size=None, rotation=None, *args, **kwargs) -> HttpResponse:
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
    field_list = [
        'location_s'
    ]
    # conn = pysolr.Solr(settings.SOLR['SERVER'])
    req = SolrConnection.search("*:*",
                                fq=["type:image", f"pk:{pk}"],
                                fl=field_list,
                                rows=1)  # ensure only one result is returned

    if req.hits == 0:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    result = req.docs[0]
    location: Optional[str] = result.get('location_s')

    if not location or location == 'None':
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    referer: str = f"{request.scheme}://{request.get_host()}"

    if region and size and rotation:
        location: str = f"{location}/{region}/{size}/{rotation}/default.jpg"

    diamm = request.META.get('HTTP_X_DIAMM')
    iiif_id = request.META.get('HTTP_X_IIIF_ID')
    headers: Dict = {'referer': referer,
                     'X-DIAMM': diamm,
                     'X-IIIF-ID': iiif_id,
                     'User-Agent': settings.DIAMM_UA}

    try:
        r = requests.get(location, stream=True, headers=headers, verify=True)
    except requests.exceptions.ConnectionError as e:
        return HttpResponse("Connection error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # If the response was a 200 (success) pass this along.
    if 200 <= r.status_code < 300:
        return HttpResponse(r.iter_content(2048), content_type=r.headers['content-type'])
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
