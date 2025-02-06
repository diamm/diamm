from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from diamm.models.site.problem_report import ProblemReport


@require_POST
def correction_submit(request):
    data = request.POST
    record_type = data.get("record_type")
    record_pk = data.get("record_pk")
    note = data.get("note")
    user = request.user
    record_type = ContentType.objects.get(
        app_label="diamm_data", model=record_type
    ).model_class()
    record = record_type.objects.get(pk=record_pk)

    d = {"record": record, "note": note, "contributor": user}

    c = ProblemReport(**d)
    c.save()

    messages.add_message(request, messages.SUCCESS, "Your submission was successful.")
    return redirect("source-detail", pk=record_pk)
