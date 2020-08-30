from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from diamm.models.site.problem_report import ProblemReport
from diamm.models.diamm_user import CustomUserModel
from django.db.models.signals import post_save

FRIENDLY_FROM = "Digital Image Archive of Medieval Music <{0}>".format(settings.DEFAULT_FROM_EMAIL)


@receiver(post_save, sender=ProblemReport)
def send_thank_you_email(sender, instance, created, **kwargs):
    if not created:
        return None

    reported_entity = instance.record
    reporter = instance.contributor

    email_address = instance.contributor.get_username()
    name = reporter.full_name
    record = reported_entity.display_name

    email_message = settings.MAIL["CORRECTION_THANK_YOU"].format(
        name=name,
        record=record,
    )

    send_mail(
        "Thank you for your contribution",
        email_message,
        FRIENDLY_FROM,
        [email_address],
        fail_silently=False
    )


# When an issue has been reported, send an e-mail to all people listed as an
# "Editor".
@receiver(post_save, sender=ProblemReport)
def send_admin_notification_email(sender, instance, created, **kwargs):
    if not created:
        return None

    reported_entity = instance.record
    reporter = instance.contributor
    report = instance.note
    name = reporter.full_name
    record = reported_entity.display_name

    if settings.DEBUG:
        recipients = [settings.ADMIN_EMAIL]
    else:
        # Send reports to all people in the 'Editors' group
        recipients = CustomUserModel.objects.filter(groups__name__in=['Editors', "Add-edit only"]).values_list("email", flat=True)

    email_message = settings.MAIL["CORRECTION_ADMIN"].format(
        name=name,
        record=record,
        report=report,
        review_url="https://{0}/admin/diamm_site/problemreport/{1}/".format(settings.HOSTNAME, instance.pk)
    )

    send_mail(
        "A new correction report is available from {0}".format(name),
        email_message,
        FRIENDLY_FROM,
        recipients,
        fail_silently=False
    )


# When an issue has been resolved, send an e-mail to the issue reporter letting them know
#  that it has been fixed.
@receiver(post_save, sender=ProblemReport)
def send_issue_resolved_message(sender, instance, created, **kwargs):
    if not instance.accepted:
        return None

    reported_entity = instance.record
    reporter = instance.contributor
    summary = instance.summary
    original_report = instance.note
    email_address = instance.contributor.get_username()

    name = reporter.full_name
    record = reported_entity.display_name

    if settings.DEBUG:
        recipient = [settings.ADMIN_EMAIL]
    else:
        recipient = [email_address]

    email_message = settings.MAIL["ISSUE_RESOLVED"].format(
        name=name,
        record=record,
        summary=summary,
        original_report=original_report
    )

    send_mail(
        "Thank you for your contribution",
        email_message,
        FRIENDLY_FROM,
        recipient,
        fail_silently=False
    )
