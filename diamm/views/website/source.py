# import pysolr
from django.db.models.expressions import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics, permissions, response, status

from diamm.helpers.solr_helpers import SolrConnection
from diamm.models import Page, Source, SourceURL
from diamm.models.data.item import Item
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.iiif.canvas import CanvasSerializer
from diamm.serializers.iiif.manifest import SourceManifestSerializer
from diamm.serializers.iiif.service import ServiceSerializer
from diamm.serializers.website.source import SourceDetailSerializer


class SourceDetail(generics.RetrieveAPIView):
    template_name = "website/source/source_detail.jinja2"
    serializer_class = SourceDetailSerializer

    def get_queryset(self):
        public_filter = {} if self.request.user.is_staff else {"public": True}
        return (
            Source.objects.filter(**public_filter)
            .select_related("archive__city__parent", "cover_image")
            .prefetch_related(
                "copyists",
                "notations",
                "links",
                "bibliographies",
                "sets",
                "identifiers",
                "authorities",
                "notes",
                "provenance__city",
                "provenance__country",
                "provenance__region",
                "contributions",
                "commentary",
            )
            .annotate(
                images_are_public=Exists(
                    Page.objects.filter(source=OuterRef("pk"), images__public=True)
                ),
                has_manifest_link=Exists(
                    SourceURL.objects.filter(
                        source=OuterRef("pk"), type=SourceURL.IIIF_MANIFEST
                    )
                ),
            )
        )


class SourceManifest(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, *args, **kwargs) -> response.Response:
        fq = ["type:source", f"pk:{pk}"]
        if not request.user.is_staff:
            fq.append("public_b:true")

        res = SolrConnection.search("*:*", fq=fq, rows=1)

        if res.hits == 0:
            return response.Response(
                status=status.HTTP_404_NOT_FOUND,
                content_type="text/html",
                data="404 Not Found",
            )

        manifest = SourceManifestSerializer(res.docs[0], context={"request": request})
        return response.Response(manifest.data)


class SourceCanvasDetail(generics.GenericAPIView):
    """
    The view handler for the IIIF Canvas resolver. Uses Solr to
     retrieve pre-indexed results for the contents of a page.
    """

    renderer_classes = (UJSONRenderer,)

    def get(self, request, source_id, page_id) -> response.Response:
        page_fields = [
            "id",
            "pk",
            "source_i",
            "numeration_s",
            "[child parentFilter=type:page childFilter=type:image]",
        ]

        # conn = pysolr.Solr(settings.SOLR['SERVER'])
        res = SolrConnection.search(
            "*:*", fq=["type:page", f"pk:{page_id}"], fl=page_fields
        )
        canvas = CanvasSerializer(res.docs[0], context={"request": request})

        return response.Response(canvas.data)


class SourceRangeDetail(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)


class SourceItemDetail(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)

    def get(self, request, source_id, item_id) -> response.Response:
        # conn = pysolr.Solr(settings.SOLR['SERVER'])

        # The pages_ii:[* TO *] query ensures we retrieve only
        # those records that have images associated with them.
        structure_query = {
            "fq": [
                "type:item",
                f"pk:{item_id}",
                f"source_i:{source_id}",
                "pages_ii:[* TO *]",
            ],
            "sort": "folio_start_ans asc",
            "rows": 10000,
        }
        structure_res = SolrConnection.search("*:*", **structure_query)
        structures = ServiceSerializer(
            structure_res.docs[0], context={"request": request}
        ).data

        return response.Response(structures)


# Linking to items directly is no longer supported; however, we can redirect to the
# source for that item.
def legacy_item_redirect(request, item_id):
    legacy_item = get_object_or_404(Item, pk=item_id)
    source_id = legacy_item.source.pk
    return redirect("source-detail", pk=source_id, permanent=True)
