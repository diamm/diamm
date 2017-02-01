from django.db import models

from diamm.models.diamm_user import CustomUserModel

class Search(models.Model):
    class Meta:
        app_label = "diamm_data"

    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    query = models.CharField(max_length=1024)
    query_type = models.CharField(max_length=1024)

    def __str__(self):
        return "{0}".format(self.query)

