from unittest.mock import patch

from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.template.loader import get_template
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from diamm.views.website.commentary import commentary_submit


class CommentarySubmissionTests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.data = {
            "record_type": "source",
            "record_pk": "123",
            "comment_type": "public",
        }

    @patch("diamm.views.website.commentary.ContentType")
    @patch("diamm.views.website.commentary.Commentary")
    @patch("diamm.views.website.commentary.messages.add_message")
    def test_blank_comments_are_rejected(self, add_message, commentary, content_type):
        for comment in (None, "", " \t\r\n "):
            with self.subTest(comment=comment):
                data = self.data.copy()
                if comment is not None:
                    data["comment"] = comment
                request = self.factory.post("/commentary/", data)
                request.user = AnonymousUser()

                response = commentary_submit(request)

                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.url, reverse("source-detail", kwargs={"pk": 123})
                )
                add_message.assert_called_with(
                    request, messages.ERROR, "Please enter a comment"
                )
                commentary.assert_not_called()
                content_type.objects.get.assert_not_called()

    @patch("diamm.views.website.commentary.ContentType")
    @patch("diamm.views.website.commentary.Commentary")
    @patch("diamm.views.website.commentary.messages.add_message")
    def test_nonblank_comment_is_saved_unchanged(
        self, add_message, commentary, content_type
    ):
        text = "  **A comment**\n"
        request = self.factory.post("/commentary/", {**self.data, "comment": text})
        request.user = AnonymousUser()
        attachment = content_type.objects.get.return_value.model_class.return_value.objects.get.return_value

        response = commentary_submit(request)

        self.assertEqual(response.status_code, 302)
        commentary.assert_called_once_with(
            comment_type=1,
            attachment=attachment,
            author=request.user,
            comment=text,
        )
        commentary.return_value.save.assert_called_once_with()
        add_message.assert_called_once_with(
            request, messages.SUCCESS, "Comment submitted successfully"
        )


class CommentaryTemplateTests(SimpleTestCase):
    def test_missing_and_empty_comment_text_render_for_public_and_private_comments(self):
        template = get_template("website/source/commentary.jinja2")
        request = RequestFactory().get("/sources/123/")
        request.user = AnonymousUser()

        for visibility in ("public", "private"):
            for text in ({}, {"comment": ""}, {"comment": "**A comment**"}):
                with self.subTest(visibility=visibility, text=text):
                    comment = {"author": "Test author", "updated": "Today", **text}
                    html = template.render(
                        {"content": {"commentary": {visibility: [comment]}}},
                        request=request,
                    )

                    self.assertIn("Test author", html)
                    if text.get("comment"):
                        self.assertIn("<strong>A comment</strong>", html)
