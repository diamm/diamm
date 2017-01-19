import serpy
from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework.reverse import reverse
from diamm.serializers import serializers


class UserCommentSerializer(serializers.ContextSerializer):
    comment = serpy.StrField()
    type_of_comment = serpy.StrField()
    attachment_type = serpy.MethodField()
    attachment_url = serpy.MethodField()
    created = serpy.MethodField()
    attachment = serpy.StrField(
        attr='attachment.display_name'
    )

    def get_attachment_type(self, obj):
        return obj.attachment._meta.model_name

    def get_attachment_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj.attachment.pk},
                       request=self.context['request'])

    def get_created(self, obj):
        return naturaltime(obj.created)


class UserSerializer(serializers.ContextSerializer):
    url = serpy.MethodField()
    last_name = serpy.StrField(
        required=False
    )
    first_name = serpy.StrField(
        required=False
    )
    full_name = serpy.StrField()
    date_joined = serpy.StrField()
    affiliation = serpy.StrField(
        required=False
    )
    superuser = serpy.BoolField(
        attr="is_superuser"
    )
    staff = serpy.BoolField(
        attr="is_staff"
    )
    comments = serpy.MethodField()

    def get_url(self, obj):
        return reverse(
            'user-account',
            request=self.context['request']
        )

    def get_comments(self, obj):
        return UserCommentSerializer(obj.commentaries.order_by('created').all()[:10],
                                     many=True,
                                     context={"request": self.context['request']}).data
