from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from diamm.models.diamm_user import CustomUserModel


class Commentary(models.Model):
    """
    Commentary about a particular object. Kept separate from
    'diamm_data' to reinforce that commentary is different than
    cataloguing data.
    """

    PRIVATE = 0
    PUBLIC = 1

    COMMENT_TYPE_OPTIONS = ((PRIVATE, "Private"), (PUBLIC, "Public"))

    comment = models.TextField()
    author = models.ForeignKey(
        CustomUserModel, related_name="commentaries", on_delete=models.CASCADE
    )
    comment_type = models.IntegerField(choices=COMMENT_TYPE_OPTIONS)

    limit = models.Q(app_label="diamm_data", model="source") | models.Q(
        app_label="diamm_data", model="page"
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, limit_choices_to=limit
    )
    object_id = models.PositiveIntegerField()
    attachment = GenericForeignKey()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "diamm_site"
        ordering = ["created"]
        verbose_name_plural = "commentaries"

    @property
    def type_of_comment(self):
        if self.comment_type is None:
            return None

        d = dict(self.COMMENT_TYPE_OPTIONS)
        return d[self.comment_type]
