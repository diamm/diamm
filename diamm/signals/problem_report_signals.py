from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from diamm.models.site.problem_report import ProblemReport
from diamm.models.diamm_user import CustomUserModel
from django.db.models.signals import post_save



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
        settings.DEFAULT_FROM_EMAIL,
        [email_address],
        fail_silently=False
    )


@receiver(post_save, sender=ProblemReport)
def send_admin_notification_email(sender, instance, created, **kwargs):
    if not created:
        return None

    reported_entity = instance.record
    reporter = instance.contributor

    name = reporter.full_name
    record = reported_entity.display_name
    recipients = CustomUserModel.objects.filter(is_staff=True).values_list("email", flat=True)

    email_message = settings.MAIL["CORRECTION_ADMIN"].format(
        name=name,
        record=record,
        review_url="https://{0}/admin/diamm_site/problemreport/{1}/".format(settings.HOSTNAME, reported_entity.pk)
    )

    send_mail(
        "A new correction report is available",
        email_message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=False
    )
