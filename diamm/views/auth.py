from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import views
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from diamm.renderers.html_renderer import HTMLRenderer


class SessionAuth(views.APIView):
    """
        A note on status codes:
        401: Users are not authenticated, but they may be given a chance to authorize.
        403: Users are authenticated (we know who they are) but for some reason they are forbidden. They
        don't get another chance.
    """
    template_name = "website/auth/login.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if not username:
            return Response({'detail': "You must supply a username"}, status=status.HTTP_401_UNAUTHORIZED)
        if not password:
            return Response({'detail': "You must supply a password"}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # If the user is logging in via the HTML interface, redirect them to their profile page.
                if isinstance(request.accepted_renderer, HTMLRenderer):
                    return HttpResponseRedirect(reverse('user-profile', kwargs={'pk': user.pk}))
                # Otherwise, return the JSON response
                return Response({'success': True})
            else:
                # user exists but is not active; forbid them access.
                return Response({}, status=status.HTTP_403_FORBIDDEN)
        else:
            # Let's check to see if they might be an old user.
            u = User.objects.filter(username=username)

            if u.count() > 0 and u.last_login is None:
                return HttpResponseRedirect('/login/update')

            # user does not exist. Assume a typo and allow them to re-authenticate
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({})


class AccountUpdate(views.APIView):
    template_name = "website/auth/update.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):
        username = request.DATA.get('username', None)
        email = request.DATA.get('email', None)

        # Check inputs
        # Send email
        # Return Response
        return HttpResponseRedirect("/login/email-sent")

    def get(self, request, *args, **kwargs):
        return Response({})


class AccountEmailSent(views.APIView):
    template_name = "website/auth/email_sent.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        return Response({})


class SessionClose(views.APIView):
    """
        POST to log out. This will clear the session ID.
    """
    template_name = "website/auth/logout.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            logout(request)
            if isinstance(request.accepted_renderer, HTMLRenderer):
                return HttpResponseRedirect(reverse("home"))
            return Response({})
        else:
            # unauthenticated users are forbidden from the logout page.
            return Response({}, status=status.HTTP_403_FORBIDDEN)
