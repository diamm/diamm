from django.db.models import Prefetch
from django.db.models.expressions import Exists, OuterRef
from rest_framework import generics

from diamm.models import (
    Composition,
    CompositionComposer,
    CompositionCycle,
    Image,
    Item,
    SourceURL,
    Voice,
)
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.composition import CompositionDetailSerializer


class CompositionDetail(generics.RetrieveAPIView):
    template_name = "website/composition/composition_detail.jinja2"
    renderer_classes = (HTMLRenderer, UJSONRenderer)
    serializer_class = CompositionDetailSerializer

    def get_queryset(self):
        public_filter = {} if self.request.user.is_staff else {"source__public": True}
        sources = (
            Item.objects.filter(**public_filter)
            .select_related("source__archive")
            .prefetch_related(
                Prefetch(
                    "voices",
                    queryset=Voice.objects.select_related(
                        "type", "clef", "mensuration"
                    ),
                )
            )
            .annotate(
                images_are_public=Exists(
                    Image.objects.filter(
                        page__source=OuterRef("source_id"), public=True
                    )
                ),
                has_manifest_link=Exists(
                    SourceURL.objects.filter(
                        source=OuterRef("source_id"), type=SourceURL.IIIF_MANIFEST
                    )
                ),
            )
            .order_by("source__sort_order")
        )
        cycle_compositions = CompositionCycle.objects.select_related(
            "composition"
        ).order_by("order")
        cycles = CompositionCycle.objects.select_related(
            "cycle__type"
        ).prefetch_related(Prefetch("cycle__compositions", queryset=cycle_compositions))

        return Composition.objects.prefetch_related(
            Prefetch("sources", queryset=sources),
            Prefetch(
                "composers",
                queryset=CompositionComposer.objects.select_related("composer"),
            ),
            Prefetch("cycles", queryset=cycles),
            "genres",
            "notes",
            "links",
        )
