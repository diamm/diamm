from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
import requests
import pysolr


def image_serve(request, pk, region=None, size=None, rotation=None, *args, **kwargs):
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
    conn = pysolr.Solr(settings.SOLR['SERVER'])
    req = conn.search("*:*",
                      fq=["type:image", "pk:{0}".format(pk)],
                      fl=field_list,
                      rows=1)  # ensure only one result is returned

    if req.hits == 0:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    result = req.docs[0]

    if 'location_s' not in result:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    location = result['location_s']
    referer = "{0}://{1}".format(request.scheme, request.get_host())

    if region and size and rotation:
        location = "{0}/{1}/{2}/{3}/default.jpg".format(location, region, size, rotation)

    diamm = request.META.get('HTTP_X_DIAMM')
    iiif_id = request.META.get('HTTP_X_IIIF_ID')

    r = requests.get(location, stream=True, headers={'referer': referer,
                                                     'X-DIAMM': diamm,
                                                     'X-IIIF-ID': iiif_id}, verify=True)

    # If the response was a 200 (success) pass this along.
    if 200 <= r.status_code < 300:
        return HttpResponse(r.iter_content(2048), content_type=r.headers['content-type'])
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
