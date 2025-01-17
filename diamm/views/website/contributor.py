from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import generics, permissions, response, status

from diamm.models.site.problem_report import ProblemReport
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.correction import CorrectionSerializer


class ContributorList(generics.ListAPIView):
    renderer_classes = (UJSONRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CorrectionSerializer

    # Takes two parameters and returns a list of accepted "problem reports" (i.e., corrections) for that record.
    # pk - The Primary Key of a particular object
    # type - The content type of the object. At present only 'source' is supported.
    #
    def get(self, request, *args, **kwargs) -> response.Response:
        pk = self.request.query_params.get("pk", None)
        objtype = self.request.query_params.get("type", None)

        if objtype not in ("source",):
            return response.Response(
                {"message": "An unexpected type argument was supplied."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pk or not type:
            return response.Response(
                {
                    "message": "You must specify both a type and an ID to retrieve commentaries"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Any non-valid query params should have been filtered out prior to reaching here.
        pk = self.request.query_params.get("pk", None)
        objtype = self.request.query_params.get("type", None)

        try:
            contenttype = ContentType.objects.get(app_label="diamm_data", model=objtype)
        except ContentType.DoesNotExist:
            raise

        queryset = ProblemReport.objects.filter(
            Q(accepted=True) & Q(object_id=pk) & Q(content_type=contenttype)
        )

        return queryset
