from rest_framework import views
from rest_framework import renderers
from rest_framework import status
from rest_framework import exceptions
from rest_framework import permissions
from rest_framework.response import Response
from diamm.renderers.html_renderer import HTMLRenderer


class ProfileView(views.APIView):
    template_name = "website/user/profile.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get_permissions(self):
        # If the requested profile matches the User's ID, show the profile.
        # Otherwise, raise the Permission Denied exception.
        if self.kwargs['pk'] == "{0}".format(self.request.user.pk):
            return (permissions.IsAuthenticated(),)
        else:
            raise exceptions.PermissionDenied

    def get(self, request, *args, **kwargs):
        return Response({})
