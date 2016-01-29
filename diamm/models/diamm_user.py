from django.contrib.auth.models import User
from django.db import models


class DIAMMUser(models.Model):
    class Meta:
        app_label = "diamm_site"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=512, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
