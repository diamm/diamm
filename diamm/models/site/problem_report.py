from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from diamm.models.diamm_user import CustomUserModel


class ProblemReport(models.Model):
    """
    The problem report functionality is dual-purpose. It serves as both the mechanism
    for reporting problems with database records, as well as the mechanism for constructing
    the "Contributors" to a particular record. A correction report is filed through a public
    interface, which is then reviewed by DIAMM staff. If it is accepted, they click the 'accepted'
    box and fill in a summary of the changes. This summary and the contributor's name
    are displayed on the record's contributors section (currently only supported by sources).
    """

    credit_help = """Use this field to acknowledge credit without tying the contribution to a specific user account. A record
    should either have a contributor or a credit acknowledgement."""

    contributor_help = """Use this field to attach a contribution to a DIAMM user account. By doing this (instead of
    simply using the 'credit' field) DIAMM users will be able to see a record of their own contributions on their account
    profile page."""

    limit = (
        models.Q(app_label="diamm_data", model="person")
        | models.Q(app_label="diamm_data", model="organization")
        | models.Q(app_label="diamm_data", model="source")
        | models.Q(app_label="diamm_data", model="composition")
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, limit_choices_to=limit
    )
    object_id = models.PositiveIntegerField()
    record = GenericForeignKey()

    note = models.TextField()
    internal_note = models.TextField(
        blank=True, null=True, help_text="DIAMM Staff notes"
    )

    # NB: To be filled out by DIAMM staff and used to build the contributions list for each record.
    accepted = models.BooleanField(
        default=False,
        help_text="If the change has been accepted as substantive by DIAMM staff, check this box. This will add the record to the linked source's Contributors area.",
    )
    summary = models.TextField(
        help_text="A summary of the change that was contributed by the user. Used to automatically build a contributor's entry for the record",
        blank=True,
        null=True,
    )

    contributor = models.ForeignKey(
        CustomUserModel,
        related_name="problem_reports",
        blank=True,
        null=True,
        help_text=contributor_help,
        on_delete=models.CASCADE,
    )
    credit = models.CharField(
        max_length=255, blank=True, null=True, help_text=credit_help
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "diamm_site"
        ordering = ("accepted",)

    def __str__(self):
        if self.contributor:
            return self.contributor.full_name
        elif self.credit:
            return self.credit
        else:
            return "Anonymous Submission"
