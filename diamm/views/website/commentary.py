from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import generics
from rest_framework import renderers
from rest_framework import response
from rest_framework import status
from rest_framework import permissions

from diamm.models.site.commentary import Commentary
from diamm.serializers.website.commentary import CommentarySerializer


class CommentaryList(generics.ListCreateAPIView):
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = CommentarySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def post(self, request, *args, **kwargs):
        data = self.request.data
        objtype = data.get('objtype')
        objpk = data.get('objpk')
        user = self.request.user
        attachment_type = ContentType.objects.get(app_label="diamm_data", model=objtype).model_class()
        attachment = attachment_type.objects.get(pk=objpk)

        comment_type = data.get('comment_type')
        comment = data.get('comment')

        d = {
            'comment_type': comment_type,
            'attachment': attachment,
            'author': user,
            'comment': comment
        }

        c = Commentary(**d)
        c.save()

        return response.Response(status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        pk = self.request.query_params.get('pk', None)
        type = self.request.query_params.get('type', None)

        if type not in ('source',):
            return response.Response({
                "message": "An unexpected type argument was supplied."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not pk or not type:
            return response.Response({
                'message': "You must specify both a type and an ID to retrieve commentaries"
            }, status=status.HTTP_400_BAD_REQUEST)

        return super(CommentaryList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        # Get all the notes for which the commentary is public OR the comment was made by the user (private)
        contenttype = None
        pk = self.request.query_params.get('pk', None)
        try:
            contenttype = ContentType.objects.get(app_label="diamm_data", model='source')
        except ContentType.DoesNotExist:
            raise

        queryset = Commentary.objects.filter(
                    (Q(content_type=contenttype) & Q(object_id=pk)) &
                    (Q(comment_type=Commentary.PUBLIC) | Q(author=self.request.user)))

        return queryset
