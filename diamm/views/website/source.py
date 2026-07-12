from django.db.models.expressions import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics, response, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    renderer_classes,
)

from diamm.helpers.solr import DEFAULT_SOLR_CLIENT
from diamm.models import Page, Source, SourceURL
from diamm.models.data.item import Item
from diamm.renderers.ujson_renderer import UJSONLDRenderer, UJSONRenderer
from diamm.serializers.iiif.canvas import CanvasSerializer
from diamm.serializers.iiif.manifest import SourceManifestSerializer
from diamm.serializers.iiif.service import ServiceSerializer
from diamm.serializers.iiif.structure import StructureSerializer
from diamm.serializers.website.source import SourceDetailSerializer

SOLR_CLIENT = DEFAULT_SOLR_CLIENT


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


@api_view(["GET", "OPTIONS"])
@authentication_classes([SessionAuthentication])
@permission_classes([])
@renderer_classes([UJSONLDRenderer])
def manifest_serve(request, pk, *args, **kwargs) -> response.Response:
    fq = ["type:source", f"pk:{pk}"]
    if not request.user.is_staff:
        fq.append("public_b:true")

    res = SOLR_CLIENT.raw_search("*:*", fq=fq, rows=1)

    if res.hits == 0:
        return response.Response(
            status=status.HTTP_404_NOT_FOUND,
            content_type="text/html",
            data="404 Not Found",
        )

    manifest = SourceManifestSerializer(res.docs[0], context={"request": request})
    return response.Response(manifest.serialized)


class SourceCanvasDetail(generics.GenericAPIView):
    """
    The view handler for the IIIF Canvas resolver. Uses Solr to
     retrieve pre-indexed results for the contents of a page.
    """

    renderer_classes = (UJSONLDRenderer,)

    def get(self, request, source_id, page_id) -> response.Response:
        res = SOLR_CLIENT.raw_search("*:*", fq=["type:image", f"page_i:{page_id}"])
        canvas = CanvasSerializer(res.docs[0], context={"request": request})

        return response.Response(canvas.serialized)


class SourceRangeDetail(generics.GenericAPIView):
    renderer_classes = (UJSONLDRenderer,)

    def get(self, request, source_id, item_id) -> response.Response:
        structure_query = {
            "fq": [
                "type:item",
                f"pk:{item_id}",
                f"source_i:{source_id}",
                "pages_ii:[* TO *]",
            ],
            "rows": 1,
        }
        structure_res = SOLR_CLIENT.raw_search("*:*", **structure_query)
        if structure_res.hits == 0:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

        structure = StructureSerializer(
            structure_res.docs[0], context={"request": request}
        ).serialized

        return response.Response(structure)


class SourceItemDetail(generics.GenericAPIView):
    renderer_classes = (UJSONRenderer,)

    def get(self, request, source_id, item_id) -> response.Response:
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
        structure_res = SOLR_CLIENT.raw_search("*:*", **structure_query)
        structures = ServiceSerializer(
            structure_res.docs[0], context={"request": request}
        ).serialized

        return response.Response(structures)


# Linking to items directly is no longer supported; however, we can redirect to the
# source for that item.
def legacy_item_redirect(request, item_id):
    legacy_item = get_object_or_404(Item, pk=item_id)
    source_id = legacy_item.source.pk
    return redirect("source-detail", pk=source_id, permanent=True)
