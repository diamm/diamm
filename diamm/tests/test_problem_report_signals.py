from unittest.mock import patch

from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from model_bakery import baker

from diamm.models.site.problem_report import ProblemReport


@override_settings(DEBUG=False)
class ProblemReportSignalTests(TestCase):
    def setUp(self) -> None:
        editors = Group.objects.create(name="Editors")
        self.editor = baker.make(
            "diamm_site.CustomUserModel", email="editor@example.org"
        )
        self.editor.groups.add(editors)
        self.contributor = baker.make(
            "diamm_site.CustomUserModel", email="contributor@example.org"
        )
        self.source = baker.make("diamm_data.Source")

    @patch("diamm.signals.problem_report_signals.send_mail")
    def test_new_report_sends_contributor_and_editor_notifications(
        self, send_mail
    ) -> None:
        report = ProblemReport.objects.create(
            record=self.source,
            note="Correct the attribution.",
            contributor=self.contributor,
        )

        self.assertEqual(send_mail.call_count, 2)
        self.assertEqual(send_mail.call_args_list[0].args[3], [self.contributor.email])
        self.assertEqual(list(send_mail.call_args_list[1].args[3]), [self.editor.email])

        report.note = "Correct the attribution and date."
        report.save()

        self.assertEqual(send_mail.call_count, 2)

    @patch("diamm.signals.problem_report_signals.send_mail")
    def test_new_report_without_contributor_notifies_only_editors(
        self, send_mail
    ) -> None:
        ProblemReport.objects.create(
            record=self.source,
            note="Correct the attribution.",
        )

        self.assertEqual(send_mail.call_count, 1)
        self.assertEqual(list(send_mail.call_args.args[3]), [self.editor.email])
