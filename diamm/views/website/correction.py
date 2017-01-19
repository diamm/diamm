from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import generics
from rest_framework import permissions
from rest_framework import response
from rest_framework import status
from rest_framework import renderers
from diamm.models.site.problem_report import ProblemReport
from diamm.serializers.website.correction import CorrectionSerializer


class CorrectionList(generics.ListCreateAPIView):
    renderer_classes = (renderers.JSONRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CorrectionSerializer

    # Create a new problem report for an object. The body of the post must contain the following parameters:
    # objtype - The content type of the object. At present only a value of 'source' is supported.
    # objpk - The PK of the object for which a problem report is being filed.
    # note - The body of the problem report.
    #
    # The user filing the problem report will be filed as the user authenticated to send the request.
    #
    def post(self, request, *args, **kwargs):
        data = self.request.data
        objtype = data.get('objtype')
        objpk = data.get('objpk')
        note = data.get('note')
        user = self.request.user
        record_type = ContentType.objects.get(app_label="diamm_data", model=objtype).model_class()
        record = record_type.objects.get(pk=objpk)

        d = {
            'record': record,
            'note': note,
            'contributor': user
        }

        c = ProblemReport(**d)
        c.save()

        return response.Response(status.HTTP_201_CREATED)

    # Takes two parameters and returns a list of accepted "problem reports" (i.e., corrections) for that record.
    # pk - The Primary Key of a particular object
    # type - The content type of the object. At present only 'source' is supported.
    #
    def get(self, request, *args, **kwargs):
        pk = self.request.query_params.get('pk', None)
        objtype = self.request.query_params.get('type', None)

        if objtype not in ('source',):
            return response.Response({
                "message": "An unexpected type argument was supplied."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not pk or not type:
            return response.Response({
                'message': "You must specify both a type and an ID to retrieve commentaries"
            }, status=status.HTTP_400_BAD_REQUEST)

        return super(CorrectionList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        # Any non-valid query params should have been filtered out prior to reaching here.
        pk = self.request.query_params.get('pk', None)
        objtype = self.request.query_params.get('type', None)

        try:
            contenttype = ContentType.objects.get(app_label="diamm_data", model=objtype)
        except ContentType.DoesNotExist:
            raise

        queryset = ProblemReport.objects.filter(
            Q(accepted=True) & Q(object_id=pk) & Q(content_type=contenttype)
        )

        return queryset
