from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework import permissions
from rest_framework import response
from rest_framework import status

from diamm.models.site.problem_report import ProblemReport
from diamm.renderers.ujson_renderer import UJSONRenderer


# Part of the problem report / correction / contributors functionality. This
# view *only* accepts incoming corrections via POST. See the models/site/problem_report
# model for further clarification, and the 'contributors' view for the corresponding
# functionality for listing contributions.
class CorrectionCreate(generics.CreateAPIView):
    renderer_classes = (UJSONRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # Create a new problem report for an object. The body of the post must contain the following parameters:
    # objtype - The content type of the object. At present only a value of 'source' is supported.
    # objpk - The PK of the object for which a problem report is being filed.
    # note - The body of the problem report.
    #
    # The user filing the problem report will be filed as the user authenticated to send the request.
    #
    def post(self, request, *args, **kwargs) -> response.Response:
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
