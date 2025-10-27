import ypres
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework.reverse import reverse

from diamm.models.data.source import Source


class UserContributionsSerializer(ypres.Serializer):
    summary = ypres.StrField(required=False)
    created = ypres.StrField()
    note = ypres.StrField(required=False)
    status = ypres.BoolField(attr="accepted")
    record = ypres.MethodField()

    def get_record(self, obj) -> dict:
        return {
            "name": obj.record.display_name,
            "url": reverse(
                "source-detail",
                kwargs={"pk": obj.record.pk},
                request=self.context["request"],
            ),
        }


class UserCommentSerializer(ypres.Serializer):
    comment = ypres.StrField()
    type_of_comment = ypres.StrField()
    attachment_type = ypres.MethodField()
    attachment_url = ypres.MethodField()
    created = ypres.MethodField()
    attachment = ypres.MethodField()

    def get_attachment(self, obj) -> str | None:
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


class UserSerializer(ypres.Serializer):
    url = ypres.MethodField()
    last_name = ypres.StrField(required=False)
    first_name = ypres.StrField(required=False)
    full_name = ypres.StrField()
    date_joined = ypres.StrField()
    affiliation = ypres.StrField(required=False)
    superuser = ypres.BoolField(attr="is_superuser")
    staff = ypres.BoolField(attr="is_staff")
    comments = ypres.MethodField()
    contributions = ypres.MethodField()
    pending_contributions = ypres.MethodField()

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
        ).serialized_many

    def get_contributions(self, obj) -> list:
        return UserContributionsSerializer(
            obj.problem_reports.filter(accepted=True),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many

    def get_pending_contributions(self, obj) -> list:
        return UserContributionsSerializer(
            obj.problem_reports.filter(accepted=False),
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many
