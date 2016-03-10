from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Contribution(models.Model):
    class Meta:
        app_label = "diamm_site"

    contributor = models.ForeignKey(User)

    limit = models.Q(app_label="diamm_data",
                     model="person") | \
            models.Q(app_label="diamm_data",
                     model="organization") | \
            models.Q(app_label="diamm_data",
                     model="source") | \
            models.Q(app_label="diamm_data",
                     model="composition")

    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    record = GenericForeignKey()

    note = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
