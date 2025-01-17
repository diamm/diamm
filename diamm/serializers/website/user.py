from typing import Optional

import serpy
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework.reverse import reverse

from diamm.models.data.source import Source
from diamm.serializers import serializers


class UserContributionsSerializer(serializers.ContextSerializer):
    summary = serpy.StrField(required=False)
    created = serpy.StrField()
    note = serpy.StrField(required=False)
    status = serpy.BoolField(attr="accepted")
    record = serpy.MethodField()

    def get_record(self, obj) -> dict:
        return {
            "name": obj.record.display_name,
            "url": reverse(
                "source-detail",
                kwargs={"pk": obj.record.pk},
                request=self.context["request"],
            ),
        }


class UserCommentSerializer(serializers.ContextSerializer):
    comment = serpy.StrField()
    type_of_comment = serpy.StrField()
    attachment_type = serpy.MethodField()
    attachment_url = serpy.MethodField()
    created = serpy.MethodField()
    attachment = serpy.MethodField()

    def get_attachment(self, obj) -> Optional[str]:
        if isinstance(obj.attachment, Source):
            return obj.attachment.display_name

        return None

    def get_attachment_type(self, obj):
        return obj.attachment._meta.model_name

    def get_attachment_url(self, obj) -> str:
        return reverse(
            "source-detail",
            kwargs={"pk": obj.attachment.pk},
            request=self.context["request"],
        )

    def get_created(self, obj):
        return naturaltime(obj.created)


class UserSerializer(serializers.ContextSerializer):
    url = serpy.MethodField()
    last_name = serpy.StrField(required=False)
    first_name = serpy.StrField(required=False)
    full_name = serpy.StrField()
    date_joined = serpy.StrField()
    affiliation = serpy.StrField(required=False)
    superuser = serpy.BoolField(attr="is_superuser")
    staff = serpy.BoolField(attr="is_staff")
    comments = serpy.MethodField()
    contributions = serpy.MethodField()
    pending_contributions = serpy.MethodField()

    def get_url(self, obj) -> str:
        return reverse("user-account", request=self.context["request"])

    def get_comments(self, obj) -> list:
        source_type = ContentType.objects.get(app_label="diamm_data", model="source")
        return UserCommentSerializer(
            obj.commentaries.order_by("created").filter(content_type=source_type.id)[
                :10
            ],
            many=True,
            context={"request": self.context["request"]},
        ).data

    def get_contributions(self, obj) -> list:
        return UserContributionsSerializer(
            obj.problem_reports.filter(accepted=True),
            many=True,
            context={"request": self.context["request"]},
        ).data

    def get_pending_contributions(self, obj) -> list:
        return UserContributionsSerializer(
            obj.problem_reports.filter(accepted=False),
            many=True,
            context={"request": self.context["request"]},
        ).data
