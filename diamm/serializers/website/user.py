import serpy
from rest_framework.reverse import reverse
from diamm.serializers import serializers


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

    def get_url(self, obj):
        return reverse(
            'user-account',
            request=self.context['request']
        )
