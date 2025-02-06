from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from diamm.models.site.commentary import Commentary


@require_POST
def commentary_submit(request):
    data = request.POST
    record_type = data.get("record_type")
    record_pk = data.get("record_pk")
    user = request.user

    attachment_type = ContentType.objects.get(
        app_label="diamm_data", model=record_type
    ).model_class()
    attachment = attachment_type.objects.get(pk=record_pk)

    comment_type = data.get("comment_type")
    ctype = 1 if comment_type == "public" else 0

    comment = data.get("comment")
    d = {
        "comment_type": ctype,
        "attachment": attachment,
        "author": user,
        "comment": comment,
    }

    c = Commentary(**d)
    c.save()
    messages.add_message(request, messages.SUCCESS, "Comment submitted successfully")
    return redirect("source-detail", pk=record_pk)
